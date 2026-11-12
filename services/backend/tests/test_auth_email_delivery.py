from __future__ import annotations

import json
from dataclasses import replace
from urllib.parse import parse_qs, urlparse

from cryptography.fernet import Fernet

from app.core.config import settings
from app.models.account_token import AccountToken
from app.models.email_outbox import EmailOutbox
from app.models.user import User
from app.services import email_delivery


class _Response:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return b'{"id":"email_api_test"}'


def _configured_settings():
    return replace(
        settings,
        environment="test",
        resend_api_key="re_test_only",
        email_from="Elevra <test@example.com>",
        email_frontend_url="http://localhost:3000",
        email_outbox_encryption_key=Fernet.generate_key().decode("ascii"),
        email_provider_timeout_seconds=1,
        email_outbox_max_attempts=5,
        email_outbox_lease_seconds=10,
    )


def _new_user(db, *, email="reset@example.com"):
    user = User(
        name="Reset Student",
        email=email,
        password_hash="not-used",
        role="student",
        is_active=True,
        email_verified=False,
    )
    db.add(user)
    db.commit()
    return user


def _run_with_test_session(monkeypatch, db):
    from app.api.v1 import auth as auth_routes

    monkeypatch.setattr(
        auth_routes,
        "dispatch_email_item",
        lambda outbox_id: email_delivery.process_outbox_item(db, outbox_id=outbox_id),
    )


def test_reset_request_does_not_create_tokens_when_email_is_disabled(client, db, monkeypatch):
    monkeypatch.setattr(email_delivery, "settings", settings)
    _new_user(db)

    known = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "reset@example.com"},
    )
    unknown = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "missing@example.com"},
    )

    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json()
    assert "has been sent" not in known.json()["message"]
    assert db.query(AccountToken).count() == 0
    assert db.query(EmailOutbox).count() == 0


def test_password_reset_request_sends_one_time_link_and_confirms_password(
    client, db, monkeypatch
):
    from app.api.v1 import auth as auth_routes

    configured = _configured_settings()
    monkeypatch.setattr(email_delivery, "settings", configured)
    _run_with_test_session(monkeypatch, db)
    _new_user(db)
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return _Response()

    monkeypatch.setattr(email_delivery, "urlopen", fake_urlopen)

    response = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "reset@example.com"},
    )

    assert response.status_code == 200
    assert "has been sent" not in response.json()["message"]
    outbox = db.query(EmailOutbox).one()
    assert outbox.status == "sent"
    assert outbox.provider_message_id == "email_api_test"
    payload = json.loads(captured["request"].data.decode("utf-8"))
    link = payload["text"].splitlines()[3]
    token = parse_qs(urlparse(link).query)["token"][0]
    assert "/reset-password?" in link

    confirm = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": token, "password": "NewSecurePass123"},
    )
    assert confirm.status_code == 200, confirm.text
    user = db.query(User).filter_by(email="reset@example.com").one()
    from app.services.auth import verify_password

    assert verify_password("NewSecurePass123", user.password_hash)
    assert db.query(AccountToken).one().used_at is not None


def test_verification_request_sends_and_consumes_one_time_link(client, db, monkeypatch):
    from app.api.v1 import auth as auth_routes

    configured = _configured_settings()
    monkeypatch.setattr(email_delivery, "settings", configured)
    _run_with_test_session(monkeypatch, db)
    user = _new_user(db, email="verify@example.com")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        return _Response()

    monkeypatch.setattr(email_delivery, "urlopen", fake_urlopen)

    response = client.post(
        "/api/v1/auth/verify-email/request",
        json={"email": "verify@example.com"},
    )
    assert response.status_code == 200
    assert "has been sent" not in response.json()["message"]
    payload = json.loads(captured["request"].data.decode("utf-8"))
    link = payload["text"].splitlines()[3]
    token = parse_qs(urlparse(link).query)["token"][0]
    assert "/verify-email?" in link

    confirm = client.post("/api/v1/auth/verify-email/confirm", json={"token": token})
    assert confirm.status_code == 200, confirm.text
    db.refresh(user)
    assert user.email_verified is True


def test_registration_queues_email_verification_when_delivery_is_enabled(
    client, db, monkeypatch
):
    configured = _configured_settings()
    monkeypatch.setattr(email_delivery, "settings", configured)
    _run_with_test_session(monkeypatch, db)
    monkeypatch.setattr(email_delivery, "urlopen", lambda *_args, **_kwargs: _Response())

    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "New Student",
            "email": "new-student@example.com",
            "password": "SecurePass123",
        },
    )

    assert response.status_code == 200, response.text
    user = db.query(User).filter_by(email="new-student@example.com").one()
    outbox = db.query(EmailOutbox).one()
    assert outbox.recipient_email == user.email
    assert outbox.purpose == "email_verification"
    assert outbox.status == "sent"
    assert db.query(AccountToken).filter_by(user_id=user.id, purpose="email_verification").count() == 1
