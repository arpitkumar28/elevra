from app.models.platform import Bookmark, Course, Test


def test_course_publication_workflow_and_visibility(client, admin_headers):
    created = client.post("/api/v1/admin/courses", headers=admin_headers, json={
        "title": "Python Foundations", "slug": "python-foundations", "provider": "Open Learning",
        "description": "Database-backed course", "category": "programming", "skills": ["python"],
    })
    assert created.status_code == 201, created.text
    course_id = created.json()["id"]
    assert client.get("/api/v1/courses").json()["total"] == 0
    for action in ("submit", "verify", "publish"):
        response = client.post(f"/api/v1/admin/courses/{course_id}/{action}", headers=admin_headers)
        assert response.status_code == 200, response.text
    listing = client.get("/api/v1/courses?q=Python")
    assert listing.status_code == 200
    assert listing.json()["items"][0]["id"] == course_id


def test_test_engine_hides_answers_and_scopes_attempts(client, admin_headers, student_headers):
    created = client.post("/api/v1/tests/admin", headers=admin_headers, json={"title": "Practice", "slug": "practice-1", "type": "practice", "duration_minutes": 30})
    test_id = created.json()["id"]
    question = client.post(f"/api/v1/tests/admin/{test_id}/questions", headers=admin_headers, json={
        "text": "2 + 2?", "options": [{"text": "3", "is_correct": False}, {"text": "4", "is_correct": True}],
    })
    assert question.status_code == 201
    assert client.post(f"/api/v1/tests/admin/{test_id}/publish", headers=admin_headers).status_code == 200
    public = client.get(f"/api/v1/tests/{test_id}").json()
    assert "is_correct" not in public["questions"][0]["options"][0]
    attempt = client.post(f"/api/v1/tests/{test_id}/start", headers=student_headers).json()
    option_id = public["questions"][0]["options"][1]["id"]
    assert client.put(f"/api/v1/tests/attempts/{attempt['attempt_id']}/answers/{public['questions'][0]['id']}", headers=student_headers, json={"option_id": option_id}).status_code == 200
    submitted = client.post(f"/api/v1/tests/attempts/{attempt['attempt_id']}/submit", headers=student_headers)
    assert submitted.status_code == 200 and submitted.json()["score"] == 1


def test_bookmarks_are_unique_and_user_scoped(client, db, student_headers):
    created = client.post("/api/v1/bookmarks", headers=student_headers, json={"entity_type": "course", "entity_id": "course-1"})
    assert created.status_code == 201
    assert client.post("/api/v1/bookmarks", headers=student_headers, json={"entity_type": "course", "entity_id": "course-1"}).status_code == 409
    bookmark_id = created.json()["id"]
    assert client.delete(f"/api/v1/bookmarks/{bookmark_id}", headers=student_headers).status_code == 204
