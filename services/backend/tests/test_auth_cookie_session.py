from app.core.config import settings


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
