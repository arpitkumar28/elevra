from dataclasses import replace

from app.core.config import settings
from app.infrastructure.security.jwt import create_refresh_token
from app.models.refresh_token import RefreshToken
from app.services.auth import hash_token_for_storage


def test_refresh_cookie_restores_and_rotates_session(client):
    registered = client.post(
        "/api/v1/auth/register",
        json={"name": "Cookie Student", "email": "cookie@example.com", "password": "SecurePass123"},
    )
    assert registered.status_code == 200, registered.text
    first_refresh = registered.json()["refresh_token"]

    cookie = registered.cookies.get("elevra_refresh")
    assert cookie == first_refresh
    set_cookie = registered.headers["set-cookie"].lower()
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie
    assert "path=/api/v1/auth" in set_cookie
    assert ("secure" in set_cookie) is (settings.environment not in {"development", "test"})

    refreshed = client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 200, refreshed.text
    first_rotation = refreshed.json()
    assert first_rotation["refresh_token"] != first_refresh
    assert client.cookies.get("elevra_refresh") == first_rotation["refresh_token"]

    restored_again = client.post("/api/v1/auth/refresh")
    assert restored_again.status_code == 200, restored_again.text
    second_rotation = restored_again.json()
    assert second_rotation["refresh_token"] != first_rotation["refresh_token"]

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {second_rotation['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "cookie@example.com"

    logout = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {second_rotation['access_token']}"},
    )
    assert logout.status_code == 200, logout.text
    assert "max-age=0" in logout.headers["set-cookie"].lower()

    revoked = client.post("/api/v1/auth/refresh")
    assert revoked.status_code == 401


def test_expired_refresh_record_is_rejected_and_cookie_is_cleared(client, db):
    registered = client.post(
        "/api/v1/auth/register",
        json={"name": "Expired Student", "email": "expired@example.com", "password": "SecurePass123"},
    )
    token = registered.json()["refresh_token"]
    row = db.query(RefreshToken).filter(RefreshToken.token_hash == hash_token_for_storage(token)).one()
    from datetime import UTC, datetime, timedelta

    row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db.commit()

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "REFRESH_TOKEN_INVALID"
    assert "max-age=0" in response.headers["set-cookie"].lower()


def test_cookie_refresh_rejects_untrusted_origin(client):
    registered = client.post(
        "/api/v1/auth/register",
        json={"name": "Origin Student", "email": "origin@example.com", "password": "SecurePass123"},
    )
    assert registered.status_code == 200

    response = client.post("/api/v1/auth/refresh", headers={"Origin": "https://attacker.example"})

    assert response.status_code == 403
    assert "max-age=0" not in response.headers.get("set-cookie", "").lower()


def test_invalid_refresh_cookie_is_removed(client):
    client.cookies.set("elevra_refresh", "not-a-valid-token", path="/api/v1/auth")

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    assert "max-age=0" in response.headers["set-cookie"].lower()


def test_production_cookie_is_cross_site_capable_but_secure(monkeypatch):
    from app.api.v1 import auth
    from starlette.responses import Response

    monkeypatch.setattr(auth, "settings", replace(settings, environment="production"))
    response = Response()
    auth._set_refresh_cookie(response, create_refresh_token("student-id"))

    header = response.headers["set-cookie"].lower()
    assert "secure" in header
    assert "samesite=none" in header


def test_configured_frontend_origin_can_send_auth_cookie(client):
    response = client.options(
        "/api/v1/auth/refresh",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_refresh_rotation_rejects_replayed_predecessor(client):
    registered = client.post(
        "/api/v1/auth/register",
        json={"name": "Replay Student", "email": "replay@example.com", "password": "SecurePass123"},
    )
    old_token = registered.json()["refresh_token"]

    rotated = client.post("/api/v1/auth/refresh", json={"refresh_token": old_token})
    assert rotated.status_code == 200
    replayed = client.post("/api/v1/auth/refresh", json={"refresh_token": old_token})

    assert replayed.status_code == 401
    assert replayed.json()["error"]["code"] == "REFRESH_TOKEN_INVALID"


def test_inactive_user_cannot_refresh_session(client, db):
    from app.models.user import User

    registered = client.post(
        "/api/v1/auth/register",
        json={"name": "Inactive Student", "email": "inactive@example.com", "password": "SecurePass123"},
    )
    user = db.query(User).filter(User.email == "inactive@example.com").one()
    user.is_active = False
    db.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "SecurePass123"},
    )
    assert login.status_code == 401

    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": registered.json()["refresh_token"]}
    )

    assert response.status_code == 401


def test_login_rate_limit_ignores_untrusted_forwarded_ip(client):
    for _ in range(10):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "missing@example.com", "password": "not-the-password"},
            headers={"X-Forwarded-For": f"198.51.100.{_ + 1}"},
        )
        assert response.status_code == 401

    limited = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "not-the-password"},
        headers={"X-Forwarded-For": "203.0.113.99"},
    )

    assert limited.status_code == 429


def test_dev_super_admin_token_is_unavailable_outside_dev(monkeypatch, client):
    from app.api.dependencies import auth as auth_dependency
    from app.api.v1.endpoints import auth as dev_auth
    from dataclasses import replace
    from app.infrastructure.security.jwt import create_access_token

    production = replace(settings, environment="production")
    monkeypatch.setattr(dev_auth, "settings", production)
    monkeypatch.setattr(auth_dependency, "settings", production)

    assert client.post("/api/v1/auth/dev-token").status_code == 404
    dev_subject_token = create_access_token(
        "00000000-0000-4000-8000-000000000001",
        {"roles": ["super_admin"], "permissions": ["users:read"]},
    )
    assert client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {dev_subject_token}"}
    ).status_code == 401


def test_production_rejects_placeholder_jwt_secret():
    import pytest
    from app.core.config import validate_security_settings

    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        validate_security_settings(replace(settings, environment="production", jwt_secret="change-me"))


def test_production_accepts_long_random_jwt_secret():
    from app.core.config import validate_security_settings

    validate_security_settings(replace(settings, environment="production", jwt_secret="x" * 64))
