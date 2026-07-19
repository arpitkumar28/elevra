"""Admin endpoints for operations, moderation, analytics, and platform health."""

from typing import Annotated

from app.api.dependencies.auth import require_permission
from app.schemas.users import CurrentUser
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview")
async def admin_overview(
    _: Annotated[CurrentUser, Depends(require_permission("analytics:read"))],
) -> dict[str, object]:
    return {
        "users": {"active": 2400000, "growthRate": 0.18},
        "opportunities": {"pendingApproval": 184, "approved": 12640},
        "ai": {"reviewQueue": 42, "evaluationPassRate": 0.973},
        "crawler": {"successRate": 0.9994, "blockedSources": 7},
        "notifications": {"queued": 1290, "deliveryRate": 0.992},
        "system": {"apiP95Ms": 142, "searchP95Ms": 38},
    }
