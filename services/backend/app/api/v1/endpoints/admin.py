"""Admin endpoints for operations, moderation, analytics, and platform health."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from app.api.dependencies.auth import require_permission
from app.db.session import get_db
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.platform import Application, AuditLog
from app.models.user import User
from app.schemas.users import CurrentUser
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview")
def admin_overview(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[CurrentUser, Depends(require_permission("analytics:read"))],
) -> dict[str, object]:
    """Return live operational metrics for the administrator workspace."""
    today = datetime.now(UTC).date()
    closing_window_end = today + timedelta(days=7)

    published_opportunities = db.query(Opportunity.id).filter(
        Opportunity.status == OpportunityStatus.published
    )
    pending_review_opportunities = db.query(Opportunity.id).filter(
        Opportunity.status == OpportunityStatus.pending_review
    )
    draft_opportunities = db.query(Opportunity.id).filter(
        Opportunity.status == OpportunityStatus.draft
    )
    closing_soon_opportunities = published_opportunities.filter(
        Opportunity.deadline >= today,
        Opportunity.deadline <= closing_window_end,
    )

    recent_activity = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .limit(8)
        .all()
    )

    return {
        "published_opportunities": published_opportunities.count(),
        "pending_review_opportunities": pending_review_opportunities.count(),
        "draft_opportunities": draft_opportunities.count(),
        "closing_soon_opportunities": closing_soon_opportunities.count(),
        "total_applications": db.query(Application.id).count(),
        "total_students": db.query(User.id).filter(
            User.role == "student",
            User.is_admin.is_(False),
            User.is_active.is_(True),
        ).count(),
        "recent_activity": [
            {
                "id": item.id,
                "action": item.action,
                "entity": item.entity,
                "entity_id": item.entity_id,
                "actor_id": item.actor_id,
                "created_at": item.created_at,
            }
            for item in recent_activity
        ],
        "generated_at": datetime.now(UTC),
    }
