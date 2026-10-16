from datetime import UTC, datetime
from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.platform import Course, CurrentAffair
from app.schemas.platform import CourseRead, CourseUpdate, CourseWrite, CurrentAffairRead, CurrentAffairUpdate, CurrentAffairWrite
from app.services.audit import record_audit
from app.services.auth import require_admin

router = APIRouter(tags=["content"])
_TRANSITIONS = {
    "draft": {"pending_review"}, "pending_review": {"verified", "rejected"},
    "verified": {"published"}, "published": {"expired"}, "rejected": set(), "expired": set(),
}


def _page(query, model, schema, page: int, page_size: int):
    total = query.order_by(None).count()
    items = query.order_by(model.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [schema.model_validate(item).model_dump(mode="json") for item in items], "page": page, "page_size": page_size, "total": total, "total_pages": ceil(total / page_size) if total else 0}


def _transition(item, target: str, db: Session, request: Request, actor_id: str, entity: str) -> None:
    if target not in _TRANSITIONS.get(item.status, set()):
        raise HTTPException(status_code=409, detail="invalid content workflow transition")
    item.status = target
    if target == "published" and hasattr(item, "published_at"):
        item.published_at = datetime.now(UTC)
    record_audit(db, action=target.upper() if target != "pending_review" else "SUBMIT", entity=entity, entity_id=item.id, actor_id=actor_id, request=request)
    db.commit(); db.refresh(item)


@router.get("/courses", response_model=dict)
def list_courses(db: Annotated[Session, Depends(get_db)], page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), q: str | None = None, category: str | None = None, difficulty: str | None = None, mode: str | None = None):
    query = db.query(Course).filter(Course.status == "published")
    if q: query = query.filter(or_(Course.title.ilike(f"%{q.strip()}%"), Course.description.ilike(f"%{q.strip()}%"), Course.provider.ilike(f"%{q.strip()}%")))
    for field, value in ((Course.category, category), (Course.difficulty, difficulty), (Course.mode, mode)):
        if value: query = query.filter(field == value)
    return _page(query, Course, CourseRead, page, page_size)


@router.get("/courses/{course_id}", response_model=CourseRead)
def get_course(course_id: str, db: Annotated[Session, Depends(get_db)]):
    item = db.query(Course).filter(Course.id == course_id, Course.status == "published").first()
    if not item: raise HTTPException(status_code=404, detail="course not found")
    return item


@router.post("/admin/courses", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseWrite, request: Request, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)):
    if db.query(Course.id).filter(Course.slug == payload.slug).first(): raise HTTPException(status_code=409, detail="slug already exists")
    item = Course(**payload.model_dump()); db.add(item); db.flush(); record_audit(db, action="CREATE", entity="course", entity_id=item.id, actor_id=admin.id, request=request); db.commit(); db.refresh(item); return item


@router.patch("/admin/courses/{course_id}", response_model=CourseRead)
def update_course(course_id: str, payload: CourseUpdate, request: Request, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)):
    item = db.get(Course, course_id)
    if not item: raise HTTPException(status_code=404, detail="course not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    record_audit(db, action="UPDATE", entity="course", entity_id=item.id, actor_id=admin.id, request=request); db.commit(); db.refresh(item); return item


@router.post("/admin/courses/{course_id}/{action}", response_model=CourseRead)
def course_workflow(course_id: str, action: str, request: Request, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)):
    target = {"submit": "pending_review", "verify": "verified", "reject": "rejected", "publish": "published", "expire": "expired"}.get(action)
    if not target: raise HTTPException(status_code=404, detail="workflow action not found")
    item = db.get(Course, course_id)
    if not item: raise HTTPException(status_code=404, detail="course not found")
    _transition(item, target, db, request, admin.id, "course"); return item


@router.get("/current-affairs", response_model=dict)
def list_current_affairs(db: Annotated[Session, Depends(get_db)], page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), q: str | None = None, category: str | None = None, published_after: datetime | None = None):
    query = db.query(CurrentAffair).filter(CurrentAffair.status == "published")
    if q: query = query.filter(or_(CurrentAffair.title.ilike(f"%{q.strip()}%"), CurrentAffair.summary.ilike(f"%{q.strip()}%")))
    if category: query = query.filter(CurrentAffair.category == category)
    if published_after: query = query.filter(CurrentAffair.published_at >= published_after)
    return _page(query, CurrentAffair, CurrentAffairRead, page, page_size)


@router.get("/current-affairs/{affair_id}", response_model=CurrentAffairRead)
def get_current_affair(affair_id: str, db: Annotated[Session, Depends(get_db)]):
    item = db.query(CurrentAffair).filter(CurrentAffair.id == affair_id, CurrentAffair.status == "published").first()
    if not item: raise HTTPException(status_code=404, detail="current affair not found")
    return item


@router.post("/admin/current-affairs", response_model=CurrentAffairRead, status_code=status.HTTP_201_CREATED)
def create_current_affair(payload: CurrentAffairWrite, request: Request, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)):
    if db.query(CurrentAffair.id).filter(CurrentAffair.slug == payload.slug).first(): raise HTTPException(status_code=409, detail="slug already exists")
    item = CurrentAffair(**payload.model_dump()); db.add(item); db.flush(); record_audit(db, action="CREATE", entity="current_affair", entity_id=item.id, actor_id=admin.id, request=request); db.commit(); db.refresh(item); return item


@router.patch("/admin/current-affairs/{affair_id}", response_model=CurrentAffairRead)
def update_current_affair(affair_id: str, payload: CurrentAffairUpdate, request: Request, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)):
    item = db.get(CurrentAffair, affair_id)
    if not item: raise HTTPException(status_code=404, detail="current affair not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    record_audit(db, action="UPDATE", entity="current_affair", entity_id=item.id, actor_id=admin.id, request=request); db.commit(); db.refresh(item); return item


@router.post("/admin/current-affairs/{affair_id}/{action}", response_model=CurrentAffairRead)
def affair_workflow(affair_id: str, action: str, request: Request, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)):
    target = {"review": "pending_review", "verify": "verified", "publish": "published", "expire": "expired", "reject": "rejected"}.get(action)
    if not target: raise HTTPException(status_code=404, detail="workflow action not found")
    item = db.get(CurrentAffair, affair_id)
    if not item: raise HTTPException(status_code=404, detail="current affair not found")
    _transition(item, target, db, request, admin.id, "current_affair"); return item
