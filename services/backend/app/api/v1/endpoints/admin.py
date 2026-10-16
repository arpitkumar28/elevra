"""Admin endpoints for operations, moderation, analytics, and platform health."""

from typing import Annotated

from app.api.dependencies.auth import require_permission
from app.schemas.users import CurrentUser
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview")
async def admin_overview(
    _: Annotated[CurrentUser, Depends(require_permission("analytics:read"))],
) -> dict[str, object]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Admin overview metrics are not connected to live operational data",
    )
