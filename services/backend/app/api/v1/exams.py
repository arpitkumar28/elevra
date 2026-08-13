from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.exam import Exam, PublicationStatus
from app.models.exam_dates import ExamDate
from app.models.exam_syllabus import ExamSyllabus
from app.schemas.exam import ExamCategory, ExamCreate, ExamPage, ExamResponse, ExamUpdate
from app.services.auth import require_admin

router = APIRouter(prefix="/exams", tags=["exams"])


def _exam_values(payload: ExamCreate | ExamUpdate, *, partial: bool = False) -> dict:
    values = payload.model_dump(exclude_unset=partial)
    for field in ("official_website", "source_url"):
        if values.get(field) is not None:
            values[field] = str(values[field])
    return values


@router.get("", response_model=ExamPage)
def list_exams(
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, min_length=1, max_length=100),
    category: ExamCategory | None = None,
):
    query = db.query(Exam).filter(Exam.status == PublicationStatus.published)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(Exam.name.ilike(term), Exam.description.ilike(term), Exam.conducting_body.ilike(term)))
    if category:
        query = query.filter(Exam.category == category.value)
    total = query.order_by(None).count()
    items = query.order_by(Exam.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ExamPage(items=items, page=page, page_size=page_size, total=total, total_pages=ceil(total / page_size) if total else 0)


@router.get("/{slug}", response_model=ExamResponse)
def get_exam(slug: str, db: Annotated[Session, Depends(get_db)]):
    exam = db.query(Exam).filter(Exam.slug == slug, Exam.status == PublicationStatus.published).first()
    if not exam:
        raise HTTPException(status_code=404, detail="exam not found")
    return exam


@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(payload: ExamCreate, db: Annotated[Session, Depends(get_db)], _admin=Depends(require_admin)):
    if db.query(Exam.id).filter(Exam.slug == payload.slug).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="slug already exists")
    exam = Exam(**_exam_values(payload))
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


@router.patch("/{exam_id}", response_model=ExamResponse)
def update_exam(exam_id: UUID, payload: ExamUpdate, db: Annotated[Session, Depends(get_db)], _admin=Depends(require_admin)):
    exam = db.query(Exam).filter(Exam.id == str(exam_id)).first()
    if not exam:
        raise HTTPException(status_code=404, detail="exam not found")
    for key, value in _exam_values(payload, partial=True).items():
        setattr(exam, key, value)
    db.commit()
    db.refresh(exam)
    return exam


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(exam_id: UUID, db: Annotated[Session, Depends(get_db)], _admin=Depends(require_admin)) -> None:
    exam = db.query(Exam).filter(Exam.id == str(exam_id)).first()
    if not exam:
        raise HTTPException(status_code=404, detail="exam not found")
    db.delete(exam)
    db.commit()


@router.get("/{slug}/syllabus")
def get_syllabus(slug: str, db: Annotated[Session, Depends(get_db)]):
    exam = db.query(Exam).filter(Exam.slug == slug, Exam.status == PublicationStatus.published).first()
    if not exam:
        raise HTTPException(status_code=404, detail="exam not found")
    return db.query(ExamSyllabus).filter(ExamSyllabus.exam_id == exam.id).order_by(ExamSyllabus.position.asc()).all()


@router.get("/{slug}/dates")
def get_dates(slug: str, db: Annotated[Session, Depends(get_db)]):
    exam = db.query(Exam).filter(Exam.slug == slug, Exam.status == PublicationStatus.published).first()
    if not exam:
        raise HTTPException(status_code=404, detail="exam not found")
    return db.query(ExamDate).filter(ExamDate.exam_id == exam.id).all()
