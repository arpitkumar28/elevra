from app.models.platform import Application, AuditLog, Bookmark
from app.models.user import User


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def _request(client, method, path, *, headers=None, json=None):
    return client.request(method, f"/api/v1/admin/content{path}", headers=headers, json=json)


def test_admin_content_requires_admin_for_lists_and_mutations(client, student_headers):
    for path in ("/queue", "/exams", "/opportunities", "/courses", "/current-affairs", "/tests"):
        assert _request(client, "GET", path).status_code == 401
        assert _request(client, "GET", path, headers=student_headers).status_code == 403
    assert _request(client, "POST", "/courses", json={}).status_code == 401
    assert _request(client, "POST", "/courses", headers=student_headers, json={}).status_code == 403


def test_exam_admin_lifecycle_filters_public_visibility_and_audit(client, admin_headers, db):
    payload = {
        "name": "National Engineering Exam",
        "slug": "national-engineering-exam",
        "category": "engineering",
        "official_website": "https://example.com/exam",
    }
    created = _request(client, "POST", "/exams", headers=admin_headers, json=payload)
    assert created.status_code == 201, created.text
    exam = created.json()
    assert exam["status"] == "draft"
    assert client.get("/api/v1/exams").json()["total"] == 0
    assert _request(client, "GET", "/exams?status=draft", headers=admin_headers).json()["total"] == 1
    assert _request(client, "GET", f"/exams/{exam['id']}", headers=admin_headers).status_code == 200

    invalid = _request(client, "PATCH", f"/exams/{exam['id']}", headers=admin_headers, json={"name": None})
    assert invalid.status_code == 422
    updated = _request(client, "PATCH", f"/exams/{exam['id']}", headers=admin_headers, json={"name": "Updated Engineering Exam"})
    assert updated.status_code == 200 and updated.json()["name"] == "Updated Engineering Exam"
    published = _request(client, "POST", f"/exams/{exam['id']}/actions/publish", headers=admin_headers)
    assert published.status_code == 200 and published.json()["status"] == "published"
    assert client.get("/api/v1/exams").json()["total"] == 1
    archived = _request(client, "POST", f"/exams/{exam['id']}/actions/archive", headers=admin_headers)
    assert archived.status_code == 200 and archived.json()["status"] == "archived"
    assert client.get("/api/v1/exams").json()["total"] == 0
    assert db.query(AuditLog).filter(AuditLog.entity == "exam").count() == 4


def test_opportunity_admin_lifecycle_and_student_record_safe_delete(client, admin_headers, db):
    created = _request(client, "POST", "/opportunities", headers=admin_headers, json={
        "title": "Software internship", "slug": "software-internship", "type": "internship",
        "organization": "Elevra", "application_url": "https://example.com/apply",
    })
    assert created.status_code == 201, created.text
    opportunity = created.json()
    assert opportunity["status"] == "draft"
    assert client.get("/api/v1/opportunities").json()["total"] == 0
    assert _request(client, "PATCH", f"/opportunities/{opportunity['id']}", headers=admin_headers, json={"type": "job"}).status_code == 200
    published = _request(client, "POST", f"/opportunities/{opportunity['id']}/actions/publish", headers=admin_headers)
    assert published.status_code == 200 and client.get("/api/v1/opportunities").json()["total"] == 1
    closed = _request(client, "POST", f"/opportunities/{opportunity['id']}/actions/close", headers=admin_headers)
    assert closed.status_code == 200 and closed.json()["status"] == "closed"

    admin_user = db.query(User).filter(User.email == "admin@example.com").one()
    db.add(Bookmark(user_id=admin_user.id, entity_type="internship", entity_id=opportunity["id"]))
    db.add(Application(user_id=admin_user.id, opportunity_id=opportunity["id"], title="Software internship"))
    db.commit()
    deleted = client.delete(f"/api/v1/opportunities/{opportunity['id']}", headers=admin_headers)
    assert deleted.status_code == 409
    assert _request(client, "GET", f"/opportunities/{opportunity['id']}", headers=admin_headers).status_code == 200
    assert db.query(AuditLog).filter(AuditLog.entity == "opportunity").count() >= 3


def test_course_and_current_affair_review_workflows_use_persisted_queue(client, admin_headers):
    course_payload = {"title": "Intro to Policy", "slug": "intro-policy", "provider": "Elevra", "skills": ["policy"]}
    course = _request(client, "POST", "/courses", headers=admin_headers, json=course_payload)
    assert course.status_code == 201, course.text
    assert client.get("/api/v1/courses").json()["total"] == 0
    assert _request(client, "PATCH", f"/courses/{course.json()['id']}", headers=admin_headers, json={"provider": None}).status_code == 422
    assert _request(client, "POST", f"/courses/{course.json()['id']}/actions/submit", headers=admin_headers).json()["status"] == "pending_review"
    assert _request(client, "GET", "/queue?status=pending_review", headers=admin_headers).json()["total"] == 1
    assert _request(client, "POST", f"/courses/{course.json()['id']}/actions/verify", headers=admin_headers).json()["status"] == "verified"
    assert _request(client, "POST", f"/courses/{course.json()['id']}/actions/publish", headers=admin_headers).json()["status"] == "published"
    assert client.get("/api/v1/courses").json()["total"] == 1

    affair_payload = {"title": "Policy update", "slug": "policy-update", "summary": "A sufficiently detailed summary.", "content": "The full current affairs item contains enough detail.", "category": "policy", "source": "Official source"}
    affair = _request(client, "POST", "/current-affairs", headers=admin_headers, json=affair_payload)
    assert affair.status_code == 201, affair.text
    assert _request(client, "POST", f"/current-affairs/{affair.json()['id']}/actions/review", headers=admin_headers).json()["status"] == "pending_review"
    assert _request(client, "POST", f"/current-affairs/{affair.json()['id']}/actions/verify", headers=admin_headers).json()["status"] == "verified"
    assert _request(client, "POST", f"/current-affairs/{affair.json()['id']}/actions/publish", headers=admin_headers).json()["status"] == "published"
    assert client.get("/api/v1/current-affairs").json()["total"] == 1


def test_test_content_questions_publication_and_safe_draft_delete(client, admin_headers):
    created = _request(client, "POST", "/tests", headers=admin_headers, json={
        "title": "Policy basics", "slug": "policy-basics", "type": "practice", "duration_minutes": 30,
    })
    assert created.status_code == 201, created.text
    test = created.json()
    test_id = test["id"]
    assert client.get("/api/v1/tests").json() == []
    assert _request(client, "PATCH", f"/tests/{test_id}", headers=admin_headers, json={"duration_minutes": None}).status_code == 422
    assert _request(client, "POST", f"/tests/{test_id}/actions/publish", headers=admin_headers).status_code == 409
    question_payload = {"text": "Which answer is correct?", "options": [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}]}
    invalid_question = question_payload | {"options": [{"text": "A"}, {"text": "B"}]}
    assert _request(client, "POST", f"/tests/{test_id}/questions", headers=admin_headers, json=invalid_question).status_code == 422
    question = _request(client, "POST", f"/tests/{test_id}/questions", headers=admin_headers, json=question_payload)
    assert question.status_code == 201
    detail = _request(client, "GET", f"/tests/{test_id}", headers=admin_headers).json()
    assert detail["questions"][0]["options"][0]["is_correct"] is True
    publish = _request(client, "POST", f"/tests/{test_id}/actions/publish", headers=admin_headers)
    assert publish.status_code == 200
    public_test = client.get(f"/api/v1/tests/{test_id}").json()
    assert "is_correct" not in public_test["questions"][0]["options"][0]
    assert len(client.get("/api/v1/tests").json()) == 1
    assert _request(client, "POST", f"/tests/{test_id}/actions/unpublish", headers=admin_headers).json()["status"] == "draft"
    assert client.get("/api/v1/tests").json() == []

    # A test with a persisted attempt is retained even after it returns to draft.
    student = client.post("/api/v1/auth/register", json={"name": "Test Student", "email": "admin-cms-student@example.com", "password": "SecurePass123"}).json()
    republished = _request(client, "POST", f"/tests/{test_id}/actions/publish", headers=admin_headers)
    assert republished.status_code == 200
    attempt = client.post(f"/api/v1/tests/{test_id}/start", headers=_headers(student["access_token"]))
    assert attempt.status_code == 201
    _request(client, "POST", f"/tests/{test_id}/actions/unpublish", headers=admin_headers)
    assert _request(client, "DELETE", f"/tests/{test_id}", headers=admin_headers).status_code == 409
