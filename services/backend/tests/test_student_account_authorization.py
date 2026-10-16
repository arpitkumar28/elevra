from app.models.platform import Notification
from app.models.user import User


def _register(client, email: str, name: str) -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "password": "SecurePass123"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_student_account_workflow_and_cross_user_isolation(client, db, admin_headers):
    student_a = _register(client, "account-a@example.com", "Student A")
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "account-a@example.com", "password": "SecurePass123"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]
    student_a = login.json()
    refresh = client.post("/api/v1/auth/refresh")
    assert refresh.status_code == 200
    student_a = refresh.json()

    student_b = _register(client, "account-b@example.com", "Student B")

    profile = client.get("/api/v1/profile", headers=_auth(student_a["access_token"]))
    assert profile.status_code == 200
    saved_profile = client.patch(
        "/api/v1/profile",
        headers=_auth(student_a["access_token"]),
        json={"display_name": "Updated A", "graduation_year": 2030},
    )
    assert saved_profile.status_code == 200
    assert saved_profile.json()["display_name"] == "Updated A"
    assert client.patch(
        "/api/v1/profile",
        headers=_auth(student_a["access_token"]),
        json={"graduation_year": 2200},
    ).status_code == 422

    bookmark = client.post(
        "/api/v1/bookmarks",
        headers=_auth(student_a["access_token"]),
        json={"entity_type": "course", "entity_id": "course-a"},
    )
    assert bookmark.status_code == 201
    assert client.post(
        "/api/v1/bookmarks",
        headers=_auth(student_a["access_token"]),
        json={"entity_type": "not-a-supported-type", "entity_id": "course-a"},
    ).status_code == 422

    application = client.post(
        "/api/v1/applications",
        headers=_auth(student_a["access_token"]),
        json={"title": "Software Intern", "organization": "Elevra Partner", "status": "saved"},
    )
    assert application.status_code == 201
    assert client.get("/api/v1/applications", headers=_auth(student_a["access_token"])).json()[0]["id"] == application.json()["id"]
    assert client.get("/api/v1/bookmarks", headers=_auth(student_a["access_token"])).json()[0]["id"] == bookmark.json()["id"]

    student_a_user = db.query(User).filter(User.email == "account-a@example.com").one()
    db.add(Notification(user_id=student_a_user.id, type="account", title="Welcome", body="Welcome to Elevra"))
    db.commit()

    test = client.post(
        "/api/v1/tests/admin",
        headers=admin_headers,
        json={"title": "Account Test", "slug": "account-test", "type": "practice", "duration_minutes": 30},
    )
    test_id = test.json()["id"]
    question = client.post(
        f"/api/v1/tests/admin/{test_id}/questions",
        headers=admin_headers,
        json={"text": "Pick one", "options": [{"text": "A", "is_correct": True}, {"text": "B"}]},
    )
    assert question.status_code == 201
    assert client.post(f"/api/v1/tests/admin/{test_id}/publish", headers=admin_headers).status_code == 200
    started = client.post(f"/api/v1/tests/{test_id}/start", headers=_auth(student_a["access_token"]))
    assert started.status_code == 201
    attempt_id = started.json()["attempt_id"]
    question_id = client.get(f"/api/v1/tests/{test_id}").json()["questions"][0]["id"]
    test_detail = client.get(f"/api/v1/tests/{test_id}").json()
    correct_option = test_detail["questions"][0]["options"][0]["id"]

    b_headers = _auth(student_b["access_token"])
    profile_b = client.get("/api/v1/profile", headers=b_headers)
    assert profile_b.json()["user_id"] != profile.json()["user_id"]
    assert client.get("/api/v1/bookmarks", headers=b_headers).json() == []
    assert client.get("/api/v1/applications", headers=b_headers).json() == []
    assert client.get("/api/v1/notifications", headers=b_headers).json() == []
    assert client.get("/api/v1/tests/attempts/history", headers=b_headers).json() == []
    assert client.get(f"/api/v1/tests/attempts/{attempt_id}", headers=b_headers).status_code == 404
    assert client.delete(f"/api/v1/bookmarks/{bookmark.json()['id']}", headers=b_headers).status_code == 404
    assert client.patch(
        f"/api/v1/applications/{application.json()['id']}", headers=b_headers, json={"status": "applied"}
    ).status_code == 404
    notification = client.get("/api/v1/notifications", headers=_auth(student_a["access_token"])).json()[0]
    assert client.post(f"/api/v1/notifications/{notification['id']}/read", headers=b_headers).status_code == 404
    assert client.put(
        f"/api/v1/tests/attempts/{attempt_id}/answers/{question_id}",
        headers=b_headers,
        json={"option_id": "arbitrary"},
    ).status_code == 404
    assert client.post(f"/api/v1/tests/attempts/{attempt_id}/submit", headers=b_headers).status_code == 404

    assert client.put(
        f"/api/v1/tests/attempts/{attempt_id}/answers/{question_id}",
        headers=_auth(student_a["access_token"]),
        json={"option_id": correct_option},
    ).status_code == 200
    attempt_detail = client.get(
        f"/api/v1/tests/attempts/{attempt_id}", headers=_auth(student_a["access_token"])
    )
    assert attempt_detail.json()["answers"] == [{"question_id": question_id, "option_id": correct_option}]
    submitted = client.post(
        f"/api/v1/tests/attempts/{attempt_id}/submit", headers=_auth(student_a["access_token"])
    )
    assert submitted.status_code == 200 and submitted.json()["score"] == 1

    notification = client.get("/api/v1/notifications", headers=_auth(student_a["access_token"])).json()[0]
    assert client.post(
        f"/api/v1/notifications/{notification['id']}/read", headers=_auth(student_a["access_token"])
    ).json()["status"] == "read"
    updated_application = client.patch(
        f"/api/v1/applications/{application.json()['id']}",
        headers=_auth(student_a["access_token"]),
        json={"status": "applied"},
    )
    assert updated_application.status_code == 200
    assert updated_application.json()["status"] == "applied"
    assert client.delete(
        f"/api/v1/bookmarks/{bookmark.json()['id']}", headers=_auth(student_a["access_token"])
    ).status_code == 204

    assert client.get("/api/v1/tests/attempts/history", headers=_auth(student_a["access_token"])).json()[0]["id"] == attempt_id
    client.cookies.set("elevra_refresh", student_a["refresh_token"], path="/api/v1/auth")
    logout = client.post(
        "/api/v1/auth/logout",
        headers=_auth(student_a["access_token"]),
        json={"refresh_token": student_a["refresh_token"]},
    )
    assert logout.status_code == 200
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": student_a["refresh_token"]}).status_code == 401


def test_student_endpoints_require_authentication(client):
    assert client.get("/api/v1/profile").status_code == 401
    assert client.get("/api/v1/bookmarks").status_code == 401
    assert client.get("/api/v1/applications").status_code == 401
    assert client.get("/api/v1/notifications").status_code == 401
    assert client.get("/api/v1/tests/attempts/history").status_code == 401
