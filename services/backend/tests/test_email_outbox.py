from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlparse

from cryptography.fernet import Fernet
from sqlalchemy import inspect

from app.core.config import settings
from app.models.account_token import AccountToken
from app.models.email_outbox import EmailOutbox
from app.models.user import User
from app.services import email_delivery
from app.services.auth import create_account_token


def _configured_email_settings():
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


class _FakeResponse:
    def __init__(self, body: bytes = b'{"id":"email_test_123"}') -> None:
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return self.body


def _user(db):
    user = User(
        name="Email Student",
        email="email-student@example.com",
        password_hash="not-used-in-this-test",
        role="student",
    )
    db.add(user)
    db.commit()
    return user


def _queued_message(db, purpose: str = "password_reset"):
    user = _user(db)
    token_row, raw_value = create_account_token(
        db,
        user,
        purpose,
        expires_in_hours=1 if purpose == "password_reset" else 24,
    )
    outbox = email_delivery.enqueue_account_email(
        db,
        account_token=token_row,
        recipient_email=user.email,
        purpose=purpose,
        token_value=raw_value,
    )
    db.commit()
    return user, token_row, raw_value, outbox


def test_email_delivery_is_disabled_without_all_required_configuration(monkeypatch):
    monkeypatch.setattr(email_delivery, "settings", settings)
    assert email_delivery.email_delivery_is_configured() is False


def test_outbox_encrypts_raw_account_token_at_rest(db, monkeypatch):
    configured = _configured_email_settings()
    monkeypatch.setattr(email_delivery, "settings", configured)

    _user_row, token_row, raw_value, outbox = _queued_message(db)

    assert outbox.status == "pending"
    assert outbox.encrypted_token != raw_value
    assert configured.email_outbox_encryption_key
    assert email_delivery._fernet().decrypt(
        outbox.encrypted_token.encode("ascii")
    ).decode("utf-8") == raw_value
    assert token_row.token_hash != raw_value
    assert db.query(EmailOutbox).filter_by(account_token_id=token_row.id).count() == 1


def test_resend_acceptance_sends_link_with_idempotency_and_erases_ciphertext(
    db, monkeypatch
):
    configured = _configured_email_settings()
    monkeypatch.setattr(email_delivery, "settings", configured)
    _user_row, token_row, raw_value, outbox = _queued_message(db)
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return _FakeResponse()

    monkeypatch.setattr(email_delivery, "urlopen", fake_urlopen)

    assert email_delivery.process_outbox_item(db, outbox_id=outbox.id) is True

    db.refresh(outbox)
    assert outbox.status == "sent"
    assert outbox.provider_message_id == "email_test_123"
    assert outbox.sent_at is not None
    assert outbox.encrypted_token is None
    assert outbox.locked_until is None
    assert captured["request"].full_url == "https://api.resend.com/emails"
    assert captured["request"].get_method() == "POST"
    assert captured["request"].get_header("Authorization") == "Bearer re_test_only"
    assert captured["request"].get_header("Idempotency-key") == f"elevra-auth-{outbox.id}"
    assert captured["timeout"] == 1

    payload = json.loads(captured["request"].data.decode("utf-8"))
    assert payload["to"] == ["email-student@example.com"]
    link = parse_qs(urlparse(payload["text"].splitlines()[2]).query)
    assert link["token"] == [raw_value]
    assert db.query(AccountToken).filter_by(id=token_row.id).one().token_hash != raw_value

    # Replaying an already-sent outbox id cannot trigger a second provider call.
    assert email_delivery.process_outbox_item(db, outbox_id=outbox.id) is False


def test_retryable_resend_failure_is_scheduled_with_bounded_backoff(db, monkeypatch):
    configured = _configured_email_settings()
    monkeypatch.setattr(email_delivery, "settings", configured)
    _user_row, _token_row, _raw_value, outbox = _queued_message(db)
    now = datetime.now(UTC)

    def fail_send(*_args, **_kwargs):
        raise email_delivery.EmailProviderError("resend_http_429", retryable=True)

    monkeypatch.setattr(email_delivery, "_send_with_resend", fail_send)

    assert email_delivery.process_outbox_item(db, outbox_id=outbox.id) is True

    db.refresh(outbox)
    assert outbox.status == "retry"
    assert outbox.attempt_count == 1
    assert outbox.last_error == "resend_http_429"
    assert outbox.encrypted_token is not None
    assert outbox.locked_until is None
    assert now + timedelta(seconds=29) < outbox.next_attempt_at < now + timedelta(seconds=32)


def test_permanent_resend_failure_invalidates_one_time_token(db, monkeypatch):
    configured = _configured_email_settings()
    monkeypatch.setattr(email_delivery, "settings", configured)
    _user_row, token_row, _raw_value, outbox = _queued_message(db)

    def fail_send(*_args, **_kwargs):
        raise email_delivery.EmailProviderError("resend_http_400", retryable=False)

    monkeypatch.setattr(email_delivery, "_send_with_resend", fail_send)

    assert email_delivery.process_outbox_item(db, outbox_id=outbox.id) is True

    db.refresh(outbox)
    db.refresh(token_row)
    assert outbox.status == "failed"
    assert outbox.encrypted_token is None
    assert outbox.last_error == "resend_http_400"
    assert token_row.used_at is not None


def test_expired_account_token_is_not_sent(db, monkeypatch):
    configured = _configured_email_settings()
    monkeypatch.setattr(email_delivery, "settings", configured)
    _user_row, token_row, _raw_value, outbox = _queued_message(db)
    token_row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db.commit()
    sent = []
    monkeypatch.setattr(email_delivery, "_send_with_resend", lambda *args: sent.append(args))

    email_delivery.process_outbox_item(db, outbox_id=outbox.id)

    db.refresh(outbox)
    assert not sent
    assert outbox.status == "failed"
    assert outbox.last_error == "account_token_invalid_or_expired"


def test_email_outbox_model_is_private_and_has_retry_indexes(db):
    indexes = {index["name"] for index in inspect(db.get_bind()).get_indexes("email_outbox")}
    assert "ix_email_outbox_status_next_attempt" in indexes
    assert "ix_email_outbox_locked_until" in indexes
