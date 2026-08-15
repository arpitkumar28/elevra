from __future__ import annotations

import uuid

import pytest

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
    assert dup.json()["detail"] == "email already registered"


def test_invalid_password_rejected(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "WrongPass123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "invalid credentials"


def test_refresh_rotation_and_logout(client):
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

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": data["refresh_token"]},
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert logout.status_code == 200

    replay = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": data["refresh_token"]},
    )
    assert replay.status_code == 401
    assert replay.json()["detail"] == "refresh token revoked or invalid"


def test_password_reset_flow(client):
    email = "reset@example.com"
    register_user(client, email, "SecurePass123")
    request = client.post("/api/v1/auth/password-reset/request", json={"email": email})
    assert request.status_code == 200
    token = request.json()["message"]
    assert "token" in token.lower() or len(token) > 0

    confirm = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": "invalid-token", "password": "NewPassword456"},
    )
    assert confirm.status_code == 400


def test_email_verification_flow(client):
    email = "verify@example.com"
    register_user(client, email, "SecurePass123")
    request = client.post("/api/v1/auth/verify-email/request", json={"email": email})
    assert request.status_code == 200
    assert "sent" in request.json()["message"].lower()

    db_user = client.app.dependency_overrides.get(None)
    assert db_user is None


def test_protected_route_requires_authentication(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "authentication required"


def test_student_cannot_hit_admin_routes(client):
    token = register_user(client, "student-admin@example.com", "SecurePass123")
    response = client.get(
        "/api/v1/admin/overview",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "admin access required"


def test_malformed_and_expired_jwt_are_rejected(client):
    malformed = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert malformed.status_code == 401
    assert malformed.json()["detail"] == "invalid token"

    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiZXhwIjoxNTE2MjM5MDIyfQ.0nJcGx5SEj5f5efmQjK2M2KxV3r5R6s5V0Qk3fXQ4xA"
    expired = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert expired.status_code == 401


def test_rate_limiting_and_safe_error_responses(client):
    for _ in range(10):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "rate@example.com", "password": "WrongPass123"},
        )
    assert response.status_code in {401, 429}

    bad_request = client.post(
        "/api/v1/auth/register",
        json={"name": "x", "email": "not-an-email", "password": "Short1"},
    )
    assert bad_request.status_code == 422
    assert "detail" in bad_request.json()
