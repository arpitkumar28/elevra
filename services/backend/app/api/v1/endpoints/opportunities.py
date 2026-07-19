"""Opportunity discovery endpoints with filtering, sorting, and pagination."""

from typing import Annotated
from uuid import uuid4

from app.api.dependencies.auth import get_current_user, require_permission
from app.core.pagination import PageMeta, PageParams, page_params
from app.domain.models.enums import OpportunityStatus, OpportunityType
from app.infrastructure.rate_limit.limiter import limiter
from app.schemas.common import PaginatedResponse
from app.schemas.opportunities import OpportunityCreate, OpportunityRead
from app.schemas.users import CurrentUser
from fastapi import APIRouter, Depends, Query, Request

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=PaginatedResponse[OpportunityRead])
@limiter.limit("60/minute")
async def list_opportunities(
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    page: Annotated[PageParams, Depends(page_params)],
    query: Annotated[str | None, Query(max_length=160)] = None,
    type: OpportunityType | None = None,
    country: Annotated[str | None, Query(max_length=80)] = None,
) -> PaginatedResponse[OpportunityRead]:
    del request, user
    data = [
        OpportunityRead(
            id="opp_scholarship_global_ai",
            type=type or OpportunityType.SCHOLARSHIP,
            status=OpportunityStatus.APPROVED,
            title=query or "Global AI Scholars Program",
            provider_name="Elevra Verified Network",
            description="Merit-based scholarship for students building practical AI projects.",
            country=country or "global",
            grade_levels=["grade_11", "grade_12", "undergraduate"],
            tags=["ai", "scholarship", "portfolio"],
            source_url="https://example.com/opportunities/global-ai-scholars",
            deadline_at="2026-10-31",
            popularity_score=0.94,
        )
    ]
    return PaginatedResponse(
        data=data,
        meta=PageMeta(page=page.page, page_size=page.page_size, total=len(data)),
        request_id=str(uuid4()),
    )


@router.post("", response_model=OpportunityRead, status_code=201)
async def create_opportunity(
    payload: OpportunityCreate,
    _: Annotated[CurrentUser, Depends(require_permission("opportunities:approve"))],
) -> OpportunityRead:
    return OpportunityRead(
        id=str(uuid4()),
        status=OpportunityStatus.PENDING_REVIEW,
        popularity_score=0,
        **payload.model_dump(),
    )
