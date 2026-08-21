from app.main import app
from fastapi.testclient import TestClient


def test_dev_token_allows_opportunity_search() -> None:
    client = TestClient(app)
    token_response = client.post("/api/v1/auth/dev-token")
    assert token_response.status_code == 200

    access_token = token_response.json()["access_token"]
    response = client.get(
        "/api/v1/opportunities",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"query": "AI scholarship", "country": "global"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["page"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["status"] == "published"
