from app.models.opportunity import Opportunity, OpportunityStatus, OpportunityType


def test_opportunity_search_uses_published_database_records(client, db) -> None:
    db.add(Opportunity(
        title="AI Scholarship", slug="ai-scholarship", type=OpportunityType.scholarship,
        organization="Elevra Partner", description="A real persisted test record.", location="global",
        status=OpportunityStatus.published,
    ))
    db.commit()
    response = client.get(
        "/api/v1/opportunities",
        params={"q": "AI scholarship", "location": "global"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["page"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["status"] == "published"
