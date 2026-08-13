from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.opportunity import Opportunity, OpportunityStatus, OpportunityType
from app.schemas.opportunity import OpportunityCreate, OpportunityPage, OpportunityResponse, OpportunityUpdate
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
):
    query = db.query(Opportunity).filter(Opportunity.status == OpportunityStatus.published)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(Opportunity.title.ilike(term), Opportunity.description.ilike(term), Opportunity.organization.ilike(term)))
    if type:
        query = query.filter(Opportunity.type == type)
    if location:
        query = query.filter(Opportunity.location.ilike(f"%{location.strip()}%"))
    if remote is not None:
        query = query.filter(Opportunity.remote == remote)
    if verified is not None:
        query = query.filter(Opportunity.verified == verified)
    total = query.order_by(None).count()
    items = query.order_by(Opportunity.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return OpportunityPage(items=items, page=page, page_size=page_size, total=total, total_pages=ceil(total / page_size) if total else 0)


@router.get("/{slug}", response_model=OpportunityResponse)
def get_opportunity(slug: str, db: Annotated[Session, Depends(get_db)]):
    opportunity = db.query(Opportunity).filter(Opportunity.slug == slug, Opportunity.status == OpportunityStatus.published).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="opportunity not found")
    return opportunity


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(payload: OpportunityCreate, db: Annotated[Session, Depends(get_db)], _admin=Depends(require_admin)):
    if db.query(Opportunity.id).filter(Opportunity.slug == payload.slug).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="slug already exists")
    opportunity = Opportunity(**_opportunity_values(payload))
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity(opportunity_id: UUID, payload: OpportunityUpdate, db: Annotated[Session, Depends(get_db)], _admin=Depends(require_admin)):
    opportunity = db.query(Opportunity).filter(Opportunity.id == str(opportunity_id)).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="opportunity not found")
    for key, value in _opportunity_values(payload, partial=True).items():
        setattr(opportunity, key, value)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(opportunity_id: UUID, db: Annotated[Session, Depends(get_db)], _admin=Depends(require_admin)) -> None:
    opportunity = db.query(Opportunity).filter(Opportunity.id == str(opportunity_id)).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="opportunity not found")
    db.delete(opportunity)
    db.commit()
