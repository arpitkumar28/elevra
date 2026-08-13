from app.models.exam import Exam, ExamCategory, PublicationStatus


def exam_payload(**overrides):
    payload = {"name": "National Engineering Exam", "slug": "national-engineering-exam", "category": "engineering", "official_website": "https://example.com/exam", "exam_date": "2027-05-01"}
    return payload | overrides


def published_exam(**overrides):
    values = {"name": "National Engineering Exam", "slug": "national-engineering-exam", "category": ExamCategory.engineering, "status": PublicationStatus.published}
    return Exam(**(values | overrides))


def test_exam_list_empty(client):
    response = client.get("/api/v1/exams")
    assert response.status_code == 200
    assert response.json() == {"items": [], "page": 1, "page_size": 20, "total": 0, "total_pages": 0}


def test_exam_list_search_category_and_pagination(client, db):
    db.add_all([published_exam(), published_exam(name="Medical Entrance", slug="medical-entrance", category=ExamCategory.medical), published_exam(name="Engineering Advanced", slug="engineering-advanced")])
    db.commit()
    response = client.get("/api/v1/exams?q=engineering&category=engineering&page_size=1")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2 and body["total_pages"] == 2 and len(body["items"]) == 1


def test_exam_detail_and_unknown_slug(client, db):
    db.add(published_exam())
    db.commit()
    assert client.get("/api/v1/exams/national-engineering-exam").status_code == 200
    assert client.get("/api/v1/exams/missing-exam").status_code == 404


def test_exam_mutation_authorization(client, admin_headers, student_headers):
    assert client.post("/api/v1/exams", json=exam_payload()).status_code == 401
    assert client.post("/api/v1/exams", json=exam_payload(), headers=student_headers).status_code == 403
    response = client.post("/api/v1/exams", json=exam_payload(), headers=admin_headers)
    assert response.status_code == 201
    exam_id = response.json()["id"]
    assert client.patch(f"/api/v1/exams/{exam_id}", json={"name": "Updated Exam"}, headers=admin_headers).status_code == 200
    assert client.delete(f"/api/v1/exams/{exam_id}", headers=admin_headers).status_code == 204


def test_exam_validation(client, admin_headers):
    assert client.post("/api/v1/exams", json=exam_payload(slug="Invalid slug", category="unknown"), headers=admin_headers).status_code == 422
    assert client.patch("/api/v1/exams/not-a-uuid", json={"name": "Updated"}, headers=admin_headers).status_code == 422
    assert client.get("/api/v1/exams?page=0").status_code == 422
