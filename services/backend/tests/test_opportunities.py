from app.models.opportunity import Opportunity, OpportunityStatus, OpportunityType


def opportunity_payload(**overrides):
    payload = {"title": "Software Internship", "slug": "software-internship", "type": "internship", "organization": "Elevra", "location": "Bengaluru", "remote": True, "application_url": "https://example.com/apply", "deadline": "2027-06-01"}
    return payload | overrides


def published_opportunity(**overrides):
    values = {"title": "Software Internship", "slug": "software-internship", "type": OpportunityType.internship, "organization": "Elevra", "location": "Bengaluru", "remote": True, "verified": True, "status": OpportunityStatus.published}
    return Opportunity(**(values | overrides))


def test_opportunity_list_filters_pagination_and_detail(client, db):
    db.add_all([published_opportunity(), published_opportunity(title="Research Fellowship", slug="research-fellowship", type=OpportunityType.fellowship, location="Delhi", remote=False, verified=False)])
    db.commit()
    response = client.get("/api/v1/opportunities?q=software&type=internship&location=bengaluru&remote=true&verified=true&page_size=1")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    page = client.get("/api/v1/opportunities?page_size=1").json()
    assert page["total"] == 2 and page["total_pages"] == 2 and len(page["items"]) == 1
    assert client.get("/api/v1/opportunities/software-internship").status_code == 200
    assert client.get("/api/v1/opportunities/not-found").status_code == 404


def test_opportunity_mutation_authorization_and_validation(client, admin_headers, student_headers):
    assert client.post("/api/v1/opportunities", json=opportunity_payload()).status_code == 401
    assert client.post("/api/v1/opportunities", json=opportunity_payload(), headers=student_headers).status_code == 403
    response = client.post("/api/v1/opportunities", json=opportunity_payload(), headers=admin_headers)
    assert response.status_code == 201
    opportunity_id = response.json()["id"]
    assert client.patch(f"/api/v1/opportunities/{opportunity_id}", json={"deadline": "not-a-date"}, headers=admin_headers).status_code == 422
    assert client.patch(f"/api/v1/opportunities/{opportunity_id}", json={"title": "Updated Opportunity"}, headers=admin_headers).status_code == 200
    assert client.delete(f"/api/v1/opportunities/{opportunity_id}", headers=admin_headers).status_code == 204
    assert client.post("/api/v1/opportunities", json=opportunity_payload(slug="Bad slug", type="invalid"), headers=admin_headers).status_code == 422
    assert client.post("/api/v1/opportunities", json=opportunity_payload(slug="invalid-work-mode", work_mode="flexible"), headers=admin_headers).status_code == 422
    assert client.get("/api/v1/opportunities?type=invalid").status_code == 422


def test_opportunity_work_mode_filters_are_distinct_and_legacy_remote_is_supported(client, db):
    db.add_all([
        published_opportunity(title="Remote role", slug="remote-role", work_mode="remote", remote=True),
        published_opportunity(title="Hybrid role", slug="hybrid-role", work_mode="hybrid", remote=False),
        published_opportunity(title="On-site role", slug="on-site-role", work_mode="on_site", remote=False),
    ])
    db.commit()

    for mode, expected_slug in (
        ("remote", "remote-role"),
        ("hybrid", "hybrid-role"),
        ("on_site", "on-site-role"),
    ):
        response = client.get(f"/api/v1/opportunities?work_mode={mode}")
        assert response.status_code == 200
        assert [item["slug"] for item in response.json()["items"]] == [expected_slug]

    legacy = client.get("/api/v1/opportunities?remote=true")
    assert legacy.status_code == 200
    assert [item["slug"] for item in legacy.json()["items"]] == ["remote-role"]
