from datetime import date
from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.opportunity import Opportunity, OpportunityStatus, OpportunityType
from app.models.platform import Application, Bookmark
from app.schemas.opportunity import OpportunityCreate, OpportunityPage, OpportunityResponse, OpportunityUpdate
from app.services.audit import record_audit
from app.services.auth import require_admin

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


def _opportunity_values(payload: OpportunityCreate | OpportunityUpdate, *, partial: bool = False) -> dict:
    values = payload.model_dump(exclude_unset=partial)
    for field in ("application_url", "source_url"):
        if values.get(field) is not None:
            values[field] = str(values[field])
    return values


@router.get("", response_model=OpportunityPage)
def list_opportunities(
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, min_length=1, max_length=100),
    type: OpportunityType | None = None,
    location: str | None = Query(None, min_length=1, max_length=255),
    remote: bool | None = None,
    verified: bool | None = None,
    deadline_after: date | None = None,
    deadline_before: date | None = None,
    sort: str = Query("newest", pattern="^(newest|deadline_soonest)$"),
):
    # Only published records appear in discovery. Draft, review, verified,
    # rejected, closed and archived records stay private to admin/history flows.
    query = db.query(Opportunity).filter(Opportunity.status == OpportunityStatus.published)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(
            Opportunity.title.ilike(term),
            Opportunity.summary.ilike(term),
            Opportunity.description.ilike(term),
            Opportunity.organization.ilike(term),
            Opportunity.eligibility.ilike(term),
        ))
    if type:
        query = query.filter(Opportunity.type == type)
    if location:
        query = query.filter(Opportunity.location.ilike(f"%{location.strip()}%"))
    if remote is not None:
        query = query.filter(Opportunity.remote == remote)
    if verified is not None:
        query = query.filter(Opportunity.verified == verified)
    if deadline_after:
        query = query.filter(Opportunity.deadline >= deadline_after)
    if deadline_before:
        query = query.filter(Opportunity.deadline <= deadline_before)

    total = query.order_by(None).count()
    ordering = (
        (Opportunity.deadline.asc().nullslast(), Opportunity.published_at.desc().nullslast())
        if sort == "deadline_soonest"
        else (Opportunity.published_at.desc().nullslast(), Opportunity.created_at.desc())
    )
    items = query.order_by(*ordering).offset((page - 1) * page_size).limit(page_size).all()
    return OpportunityPage(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{slug}", response_model=OpportunityResponse)
def get_opportunity(slug: str, db: Annotated[Session, Depends(get_db)]):
    # A closed listing remains readable for saved links and application history.
    opportunity = db.query(Opportunity).filter(
        or_(Opportunity.slug == slug, Opportunity.id == slug),
        Opportunity.status.in_((OpportunityStatus.published, OpportunityStatus.closed)),
    ).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="opportunity not found")
    return opportunity


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(payload: OpportunityCreate, request: Request, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)):
    if db.query(Opportunity.id).filter(Opportunity.slug == payload.slug).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="slug already exists")
    opportunity = Opportunity(**_opportunity_values(payload))
    opportunity.status = OpportunityStatus.draft
    opportunity.verified = False
    db.add(opportunity)
    db.flush()
    record_audit(db, action="CREATE", entity="opportunity", entity_id=opportunity.id, actor_id=admin.id, request=request)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity(opportunity_id: UUID, payload: OpportunityUpdate, request: Request, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)):
    opportunity = db.query(Opportunity).filter(Opportunity.id == str(opportunity_id)).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="opportunity not found")
    if opportunity.status not in (OpportunityStatus.draft, OpportunityStatus.rejected):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft or rejected opportunities can be edited. Use the review workflow for other statuses.",
        )
    for key, value in _opportunity_values(payload, partial=True).items():
        setattr(opportunity, key, value)
    record_audit(db, action="UPDATE", entity="opportunity", entity_id=opportunity.id, actor_id=admin.id, request=request)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(opportunity_id: UUID, request: Request, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)) -> None:
    opportunity = db.query(Opportunity).filter(Opportunity.id == str(opportunity_id)).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="opportunity not found")
    linked = db.query(Application.id).filter(Application.opportunity_id == opportunity.id).first()
    bookmarked = db.query(Bookmark.id).filter(
        Bookmark.entity_id == opportunity.id,
        Bookmark.entity_type.in_((
            "opportunity", "job", "internship", "scholarship", "competition",
            "fellowship", "hackathon", "research", "bootcamp", "event",
        )),
    ).first()
    if linked or bookmarked:
        raise HTTPException(status_code=409, detail="opportunity has student records; archive it instead")
    record_audit(db, action="DELETE", entity="opportunity", entity_id=opportunity.id, actor_id=admin.id, request=request)
    db.delete(opportunity)
    db.commit()
