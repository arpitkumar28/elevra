from app.models.opportunity import Opportunity, OpportunityStatus, OpportunityType


def _published_opportunity(db):
    item = Opportunity(
        title="Data Analyst Internship",
        slug="data-analyst-internship",
        type=OpportunityType.internship,
        organization="Elevra",
        application_url="https://example.com/apply",
        source_name="Elevra Careers",
        source_url="https://example.com/source",
        status=OpportunityStatus.published,
        verified=True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def test_student_can_track_published_opportunity_and_view_status_history(client, student_headers, db):
    opportunity = _published_opportunity(db)
    created = client.post(
        "/api/v1/applications",
        headers=student_headers,
        json={
            "opportunity_id": opportunity.id,
            "title": "Client supplied title must not win",
            "external_url": "https://attacker.example",
        },
    )
    assert created.status_code == 201, created.text
    application = created.json()
    assert application["status"] == "saved"
    assert application["title"] == opportunity.title
    assert application["organization"] == opportunity.organization
    assert application["external_url"] == opportunity.application_url

    duplicate = client.post(
        "/api/v1/applications",
        headers=student_headers,
        json={"opportunity_id": opportunity.id},
    )
    assert duplicate.status_code == 409

    updated = client.patch(
        f"/api/v1/applications/{application['id']}",
        headers=student_headers,
        json={
            "status": "applied",
            "status_note": "Submitted on the employer website.",
            "follow_up_date": "2027-01-10",
        },
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["status"] == "applied"
    assert updated.json()["applied_at"] is not None
    assert updated.json()["follow_up_date"] == "2027-01-10"

    events = client.get(
        f"/api/v1/applications/{application['id']}/events",
        headers=student_headers,
    )
    assert events.status_code == 200
    assert [event["new_status"] for event in events.json()] == ["saved", "applied"]
    assert events.json()[-1]["note"] == "Submitted on the employer website."

    invalid = client.patch(
        f"/api/v1/applications/{application['id']}",
        headers=student_headers,
        json={"status": "saved"},
    )
    assert invalid.status_code == 409


def test_student_cannot_track_unpublished_or_access_another_users_history(
    client, student_headers, admin_headers, db
):
    private_opportunity = Opportunity(
        title="Private internship",
        slug="private-internship",
        type=OpportunityType.internship,
        organization="Elevra",
        application_url="https://example.com/apply",
        source_name="Elevra Careers",
        source_url="https://example.com/source",
        status=OpportunityStatus.draft,
    )
    db.add(private_opportunity)
    db.commit()

    rejected = client.post(
        "/api/v1/applications",
        headers=student_headers,
        json={"opportunity_id": private_opportunity.id},
    )
    assert rejected.status_code == 409

    public_opportunity = _published_opportunity(db)
    created = client.post(
        "/api/v1/applications",
        headers=student_headers,
        json={"opportunity_id": public_opportunity.id},
    )
    assert created.status_code == 201, created.text

    denied = client.get(
        f"/api/v1/applications/{created.json()['id']}/events",
        headers=admin_headers,
    )
    assert denied.status_code == 404
