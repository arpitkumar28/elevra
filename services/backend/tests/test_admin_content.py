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


def test_every_admin_mutation_rejects_anonymous_and_student_sessions(client, admin_headers, student_headers):
    exam = _request(client, "POST", "/exams", headers=admin_headers, json={
        "name": "Access Control Exam", "slug": "access-control-exam", "category": "other",
    }).json()
    opportunity = _request(client, "POST", "/opportunities", headers=admin_headers, json={
        "title": "Access Control Job", "slug": "access-control-job", "type": "job",
    }).json()
    course = _request(client, "POST", "/courses", headers=admin_headers, json={
        "title": "Access Control Course", "slug": "access-control-course", "provider": "Elevra",
    }).json()
    affair = _request(client, "POST", "/current-affairs", headers=admin_headers, json={
        "title": "Access Control Affairs", "slug": "access-control-affairs",
        "summary": "This summary is long enough for validation.",
        "content": "This article body is long enough for validation.",
        "category": "policy", "source": "Official source",
    }).json()
    test = _request(client, "POST", "/tests", headers=admin_headers, json={
        "title": "Access Control Test", "slug": "access-control-test", "type": "practice",
        "duration_minutes": 20,
    }).json()
    question = _request(client, "POST", f"/tests/{test['id']}/questions", headers=admin_headers, json={
        "text": "Pick one", "options": [{"text": "Correct", "is_correct": True}, {"text": "Wrong"}],
    }).json()
    mutations = [
        ("PATCH", f"/exams/{exam['id']}", {"name": "Changed exam"}),
        ("PATCH", f"/opportunities/{opportunity['id']}", {"title": "Changed job"}),
        ("PATCH", f"/courses/{course['id']}", {"title": "Changed course"}),
        ("PATCH", f"/current-affairs/{affair['id']}", {"title": "Changed affairs"}),
        ("PATCH", f"/tests/{test['id']}", {"title": "Changed test"}),
        ("POST", f"/exams/{exam['id']}/actions/publish", None),
        ("POST", f"/opportunities/{opportunity['id']}/actions/publish", None),
        ("POST", f"/courses/{course['id']}/actions/submit", None),
        ("POST", f"/current-affairs/{affair['id']}/actions/review", None),
        ("POST", f"/tests/{test['id']}/actions/publish", None),
        ("PUT", f"/tests/{test['id']}/questions/{question['id']}", {
            "text": "Changed question", "options": [{"text": "Correct", "is_correct": True}, {"text": "Wrong"}],
        }),
        ("DELETE", f"/tests/{test['id']}/questions/{question['id']}", None),
        ("DELETE", f"/tests/{test['id']}", None),
    ]
    for method, path, payload in mutations:
        assert _request(client, method, path, json=payload).status_code == 401, (method, path)
        assert _request(client, method, path, headers=student_headers, json=payload).status_code == 403, (method, path)


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


def test_opportunity_admin_review_publish_close_lifecycle(client, admin_headers, db):
    created = _request(client, "POST", "/opportunities", headers=admin_headers, json={
        "title": "Software internship",
        "slug": "software-internship",
        "type": "internship",
        "organization": "Elevra",
        "summary": "A paid software internship opportunity.",
        "description": "Work with the platform engineering team on production software.",
        "application_url": "https://example.com/apply",
        "source_name": "Elevra Careers",
        "source_url": "https://example.com/source",
    })
    assert created.status_code == 201, created.text
    opportunity = created.json()
    assert opportunity["status"] == "draft"
    assert client.get("/api/v1/opportunities").json()["total"] == 0

    submitted = _request(
        client, "POST", f"/opportunities/{opportunity['id']}/actions/submit",
        headers=admin_headers,
    )
    assert submitted.status_code == 200 and submitted.json()["status"] == "pending_review"
    queue = _request(client, "GET", "/queue?status=pending_review", headers=admin_headers).json()
    assert any(item["id"] == opportunity["id"] and item["kind"] == "opportunities" for item in queue["items"])

    changed = _request(
        client, "POST", f"/opportunities/{opportunity['id']}/actions/request-changes",
        headers=admin_headers,
        json={"review_note": "Please add the official eligibility details."},
    )
    assert changed.status_code == 200
    assert changed.json()["status"] == "draft"
    assert changed.json()["review_note"] == "Please add the official eligibility details."

    resubmitted = _request(
        client, "POST", f"/opportunities/{opportunity['id']}/actions/submit",
        headers=admin_headers,
    )
    assert resubmitted.status_code == 200 and resubmitted.json()["status"] == "pending_review"
    approved = _request(
        client, "POST", f"/opportunities/{opportunity['id']}/actions/approve",
        headers=admin_headers,
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "verified"
    assert approved.json()["verified"] is True
    assert approved.json()["source_checked_at"]

    published = _request(
        client, "POST", f"/opportunities/{opportunity['id']}/actions/publish",
        headers=admin_headers,
    )
    assert published.status_code == 200 and published.json()["status"] == "published"
    assert client.get("/api/v1/opportunities").json()["total"] == 1
    closed = _request(
        client, "POST", f"/opportunities/{opportunity['id']}/actions/close",
        headers=admin_headers,
    )
    assert closed.status_code == 200 and closed.json()["status"] == "closed"
    assert client.get("/api/v1/opportunities").json()["total"] == 0
    assert client.get(f"/api/v1/opportunities/{opportunity['id']}").status_code == 200

    admin_user = db.query(User).filter(User.email == "admin@example.com").one()
    db.add(Bookmark(user_id=admin_user.id, entity_type="internship", entity_id=opportunity["id"]))
    db.add(Application(user_id=admin_user.id, opportunity_id=opportunity["id"], title="Software internship"))
    db.commit()
    deleted = client.delete(f"/api/v1/opportunities/{opportunity['id']}", headers=admin_headers)
    assert deleted.status_code == 409
    assert db.query(AuditLog).filter(AuditLog.entity == "opportunity").count() >= 5


def test_opportunity_submission_requires_source_and_application_details(client, admin_headers):
    created = _request(client, "POST", "/opportunities", headers=admin_headers, json={
        "title": "Incomplete listing",
        "slug": "incomplete-listing",
        "type": "job",
    })
    assert created.status_code == 201, created.text
    response = _request(
        client, "POST", f"/opportunities/{created.json()['id']}/actions/submit",
        headers=admin_headers,
    )
    assert response.status_code == 422


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


def test_test_content_questions_publication_and_safe_draft_delete(client, admin_headers, db):
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
    edited_question = question_payload | {"text": "Updated question text"}
    assert _request(client, "PUT", f"/tests/{test_id}/questions/{question.json()['id']}", headers=admin_headers, json=edited_question).status_code == 200
    detail = _request(client, "GET", f"/tests/{test_id}", headers=admin_headers).json()
    assert detail["questions"][0]["text"] == "Updated question text"
    assert detail["questions"][0]["options"][0]["is_correct"] is True
    question_audits = db.query(AuditLog).filter(AuditLog.entity == "test", AuditLog.entity_id == test_id).all()
    assert {entry.action for entry in question_audits} >= {"CREATE_QUESTION", "UPDATE_QUESTION"}
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


def test_admin_overview_uses_live_opportunity_and_application_data(client, admin_headers, db):
    from datetime import UTC, datetime, timedelta

    from app.models.opportunity import Opportunity, OpportunityStatus, OpportunityType

    admin_user = db.query(User).filter(User.email == "admin@example.com").one()
    today = datetime.now(UTC).date()
    published = Opportunity(
        title="Closing soon internship",
        slug="closing-soon-internship",
        type=OpportunityType.internship,
        organization="Elevra",
        application_url="https://example.com/apply",
        source_name="Official careers",
        source_url="https://example.com/source",
        status=OpportunityStatus.published,
        verified=True,
        deadline=today + timedelta(days=3),
    )
    pending = Opportunity(
        title="Pending internship",
        slug="pending-internship",
        type=OpportunityType.internship,
        organization="Elevra",
        application_url="https://example.com/pending",
        source_name="Official careers",
        source_url="https://example.com/pending-source",
        status=OpportunityStatus.pending_review,
    )
    draft = Opportunity(
        title="Draft internship",
        slug="draft-internship",
        type=OpportunityType.internship,
        organization="Elevra",
        status=OpportunityStatus.draft,
    )
    db.add_all([published, pending, draft])
    db.flush()
    db.add(Application(user_id=admin_user.id, opportunity_id=published.id, title=published.title))
    db.add(AuditLog(
        actor_id=admin_user.id,
        action="PUBLISH",
        entity="opportunity",
        entity_id=published.id,
    ))
    db.commit()

    response = client.get("/api/v1/admin/overview", headers=admin_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["published_opportunities"] == 1
    assert data["pending_review_opportunities"] == 1
    assert data["draft_opportunities"] == 1
    assert data["closing_soon_opportunities"] == 1
    assert data["total_applications"] == 1
    assert data["total_students"] == 0
    assert data["recent_activity"][0]["action"] == "PUBLISH"
