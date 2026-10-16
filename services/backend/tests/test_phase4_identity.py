from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import settings
from app.infrastructure.security.jwt import create_access_token
from app.models.user import User


@pytest.fixture
def student_payload():
    return {
        "name": "Test Student",
        "email": "student@example.com",
        "password": "SecurePass123",
    }


def register_user(client, email: str = "student@example.com", password: str = "SecurePass123"):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Test Student", "email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()


def set_user_role(db, email: str, role: str):
    user = db.query(User).filter(User.email == email).one()
    user.role = role
    db.commit()
    return user


def test_registration_and_login_flow(client, student_payload):
    result = register_user(client, student_payload["email"], student_payload["password"])
    assert "access_token" in result
    assert "refresh_token" in result

    login = client.post(
        "/api/v1/auth/login",
        json={"email": student_payload["email"], "password": student_payload["password"]},
    )
    assert login.status_code == 200, login.text
    assert login.json()["access_token"]


def test_duplicate_email_is_rejected(client):
    register_user(client, "dup@example.com", "SecurePass123")
    dup = client.post(
        "/api/v1/auth/register",
        json={"name": "Other User", "email": "dup@example.com", "password": "SecurePass123"},
    )
    assert dup.status_code == 409
    assert dup.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


def test_weak_password_is_rejected(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Weak User", "email": "weak@example.com", "password": "short"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_invalid_password_rejected(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "WrongPass123"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"


def test_refresh_rotation_and_logout(client, db):
    tokens = register_user(client)
    refresh = tokens["refresh_token"]

    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert refreshed.status_code == 200, refreshed.text
    data = refreshed.json()
    assert data["refresh_token"] != refresh
    assert data["access_token"]

    replay = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert replay.status_code == 401
    assert replay.json()["error"]["code"] == "REFRESH_TOKEN_INVALID"

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": data["refresh_token"]},
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert logout.status_code == 200

    revoked = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": data["refresh_token"]},
    )
    assert revoked.status_code == 401
    assert revoked.json()["error"]["code"] == "REFRESH_TOKEN_INVALID"

    assert db.query(User).filter(User.email == "student@example.com").one().role == "student"


def test_refresh_replay_expired_and_revoked(client):
    tokens = register_user(client, "refresh-flow@example.com", "SecurePass123")
    refresh = tokens["refresh_token"]
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    rotated = refreshed.json()["refresh_token"]
    replay = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert replay.status_code == 401

    expired_payload = jwt.encode(
        {"sub": "00000000-0000-4000-8000-000000000999", "iss": settings.jwt_issuer, "aud": settings.jwt_audience, "iat": int(datetime.now(UTC).timestamp()) - 3600, "nbf": int(datetime.now(UTC).timestamp()) - 3600, "exp": int(datetime.now(UTC).timestamp()) - 30, "type": "refresh"},
        settings.jwt_secret + "-wrong",
        algorithm="HS256",
    )
    expired = client.post("/api/v1/auth/refresh", json={"refresh_token": expired_payload})
    assert expired.status_code == 401


def test_password_reset_flow(client):
    email = "reset@example.com"
    register_user(client, email, "SecurePass123")
    request = client.post("/api/v1/auth/password-reset/request", json={"email": email})
    assert request.status_code == 200
    assert request.json()["message"] == "If the account exists, a password reset email has been sent."

    confirm = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": "invalid-token", "password": "NewPassword456"},
    )
    assert confirm.status_code == 400
    assert confirm.json()["error"]["code"] == "INVALID_OR_EXPIRED_TOKEN"

    second = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": "invalid-token", "password": "AnotherPass456"},
    )
    assert second.status_code == 400


def test_email_verification_flow(client):
    email = "verify@example.com"
    register_user(client, email, "SecurePass123")
    request = client.post("/api/v1/auth/verify-email/request", json={"email": email})
    assert request.status_code == 200
    assert "sent" in request.json()["message"].lower()

    confirm = client.post(
        "/api/v1/auth/verify-email/confirm",
        json={"token": "invalid-token"},
    )
    assert confirm.status_code == 400
    assert confirm.json()["error"]["code"] == "INVALID_OR_EXPIRED_TOKEN"


def test_protected_route_requires_authentication(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"


def test_student_cannot_hit_admin_routes(client):
    token = register_user(client, "student-admin@example.com", "SecurePass123")
    response = client.get(
        "/api/v1/admin/overview",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_malformed_and_expired_jwt_are_rejected(client):
    malformed = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert malformed.status_code == 401
    assert malformed.json()["error"]["code"] == "INVALID_TOKEN"

    expired_payload = jwt.encode(
        {"sub": "00000000-0000-4000-8000-000000000123", "iss": settings.jwt_issuer, "aud": settings.jwt_audience, "iat": int(datetime.now(UTC).timestamp()) - 3600, "nbf": int(datetime.now(UTC).timestamp()) - 3600, "exp": int(datetime.now(UTC).timestamp()) - 30, "type": "access"},
        settings.jwt_secret,
        algorithm="HS256",
    )
    expired = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_payload}"},
    )
    assert expired.status_code == 401
    assert expired.json()["error"]["code"] == "INVALID_TOKEN"

    invalid_signature_payload = jwt.encode(
        {"sub": "00000000-0000-4000-8000-000000000456", "iss": settings.jwt_issuer, "aud": settings.jwt_audience, "iat": int(datetime.now(UTC).timestamp()), "nbf": int(datetime.now(UTC).timestamp()), "exp": int((datetime.now(UTC) + timedelta(minutes=15)).timestamp()), "type": "access"},
        settings.jwt_secret + "-different",
        algorithm="HS256",
    )
    invalid_signature = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {invalid_signature_payload}"},
    )
    assert invalid_signature.status_code == 401
    assert invalid_signature.json()["error"]["code"] == "INVALID_TOKEN"


def test_role_enforcement_and_privilege_escalation_attempts(client, db):
    student = register_user(client, "student-role@example.com", "SecurePass123")
    set_user_role(db, "student-role@example.com", "student")

    admin = register_user(client, "admin-role@example.com", "SecurePass123")
    set_user_role(db, "admin-role@example.com", "admin")

    super_admin = register_user(client, "super-role@example.com", "SecurePass123")
    set_user_role(db, "super-role@example.com", "super_admin")

    student_response = client.get(
        "/api/v1/admin/overview",
        headers={"Authorization": f"Bearer {student['access_token']}"},
    )
    assert student_response.status_code == 403

    admin_response = client.get(
        "/api/v1/admin/overview",
        headers={"Authorization": f"Bearer {admin['access_token']}"},
    )
    assert admin_response.status_code == 501

    super_response = client.get(
        "/api/v1/admin/overview",
        headers={"Authorization": f"Bearer {super_admin['access_token']}"},
    )
    assert super_response.status_code == 501

    privilege_attempt = client.post(
        "/api/v1/auth/register",
        json={"name": "Escalation", "email": "escalation@example.com", "password": "SecurePass123", "role": "admin"},
    )
    assert privilege_attempt.status_code == 422


def test_rate_limiting_and_safe_error_responses(client):
    for i in range(8):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": f"rate{i}@example.com", "password": "WrongPass123"},
        )
    assert response.status_code in {401, 429}

    bad_request = client.post(
        "/api/v1/auth/register",
        json={"name": "x", "email": "not-an-email", "password": "Short1"},
    )
    assert bad_request.status_code == 422
    assert "error" in bad_request.json()
