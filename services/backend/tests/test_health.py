from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@app.get("/api/v1/__test/cors-error", include_in_schema=False)
def _raise_uncaught_error() -> None:
    raise RuntimeError("test-only failure")


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_cors_headers_are_present_on_unhandled_server_errors() -> None:
    test_client = TestClient(app, raise_server_exceptions=False)
    response = test_client.get(
        "/api/v1/__test/cors-error",
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == 500
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"
    assert response.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"


def test_validation_errors_do_not_echo_submitted_password(client) -> None:
    submitted_password = "DoNotEchoThisPassword123!" * 8
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student@example.com", "password": submitted_password},
    )

    assert response.status_code == 422
    assert submitted_password not in response.text


def test_readiness_fails_closed_without_database(client, monkeypatch) -> None:
    from app.api.v1 import health

    monkeypatch.setattr(health, "check_database", lambda: False)
    monkeypatch.setattr(health, "check_redis", lambda: True)

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "service": "backend",
        "dependencies": {
            "postgresql": {"status": "unavailable"},
            "redis": {"status": "ok"},
        },
    }


def test_readiness_fails_closed_without_redis(client, monkeypatch) -> None:
    from app.api.v1 import health

    monkeypatch.setattr(health, "check_database", lambda: True)
    monkeypatch.setattr(health, "check_redis", lambda: False)

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json()["dependencies"]["redis"]["status"] == "unavailable"
