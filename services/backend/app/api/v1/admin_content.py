"""Administrator-only content management over the persisted platform models."""

from datetime import UTC, datetime
from math import ceil
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.exam import Exam, PublicationStatus as ExamStatus
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.platform import (
    Course,
    CurrentAffair,
    Question,
    QuestionOption,
    Test,
    TestAttempt,
)
from app.schemas.exam import ExamCategory, ExamCreate, ExamResponse, ExamUpdate
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityResponse,
    OpportunityType,
    OpportunityUpdate,
)
from app.schemas.platform import (
    ContentStatus,
    CourseRead,
    CourseUpdate,
    CourseWrite,
    CurrentAffairRead,
    CurrentAffairUpdate,
    CurrentAffairWrite,
    QuestionWrite,
    TestAdminRead,
    TestType,
    TestUpdate,
    TestWrite,
)
from app.services.audit import record_audit
from app.services.auth import require_admin

router = APIRouter(prefix="/admin/content", tags=["admin-content"])

KINDS = ("exams", "opportunities", "courses", "current-affairs", "tests")
ENTITY_NAMES = {
    "exams": "exam",
    "opportunities": "opportunity",
    "courses": "course",
    "current-affairs": "current_affair",
    "tests": "test",
}
MODELS = {
    "exams": Exam,
    "opportunities": Opportunity,
    "courses": Course,
    "current-affairs": CurrentAffair,
    "tests": Test,
}
READ_SCHEMAS = {
    "exams": ExamResponse,
    "opportunities": OpportunityResponse,
    "courses": CourseRead,
    "current-affairs": CurrentAffairRead,
    "tests": TestAdminRead,
}
CREATE_SCHEMAS = {
    "exams": ExamCreate,
    "opportunities": OpportunityCreate,
    "courses": CourseWrite,
    "current-affairs": CurrentAffairWrite,
    "tests": TestWrite,
}
UPDATE_SCHEMAS = {
    "exams": ExamUpdate,
    "opportunities": OpportunityUpdate,
    "courses": CourseUpdate,
    "current-affairs": CurrentAffairUpdate,
    "tests": TestUpdate,
}


def _kind(kind: str) -> str:
    if kind not in KINDS:
        raise HTTPException(status_code=404, detail="content type not found")
    return kind


def _validate_payload(schema, payload: dict):
    try:
        return schema.model_validate(payload)
    except ValidationError as exc:
        raise RequestValidationError(exc.errors(include_input=False, include_context=False)) from exc


def _row(kind: str, item, db: Session) -> dict:
    if kind != "tests":
        return READ_SCHEMAS[kind].model_validate(item).model_dump(mode="json")
    questions = db.query(Question).filter(Question.test_id == item.id).order_by(Question.position, Question.id).all()
    return {
        "id": item.id,
        "title": item.title,
        "slug": item.slug,
        "description": item.description,
        "type": item.type,
        "duration_minutes": item.duration_minutes,
        "status": item.status,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "questions": [
            {
                "id": question.id,
                "text": question.text,
                "explanation": question.explanation,
                "position": question.position,
                "options": [
                    {
                        "id": option.id,
                        "text": option.text,
                        "position": option.position,
                        "is_correct": option.is_correct,
                    }
                    for option in db.query(QuestionOption)
                    .filter(QuestionOption.question_id == question.id)
                    .order_by(QuestionOption.position, QuestionOption.id)
                ],
            }
            for question in questions
        ],
    }


def _find(kind: str, content_id: str, db: Session):
    model = MODELS[kind]
    item = db.query(model).filter(or_(model.id == content_id, model.slug == content_id)).first()
    if item is None:
        raise HTTPException(status_code=404, detail=f"{kind} item not found")
    return item


def _base_query(kind: str, db: Session, q: str | None, category: str | None, type_filter: str | None):
    model = MODELS[kind]
    query = db.query(model)
    if q:
        term = f"%{q.strip()}%"
        fields = {
            "exams": (Exam.name, Exam.description, Exam.conducting_body),
            "opportunities": (Opportunity.title, Opportunity.description, Opportunity.organization),
            "courses": (Course.title, Course.description, Course.provider),
            "current-affairs": (CurrentAffair.title, CurrentAffair.summary, CurrentAffair.content),
            "tests": (Test.title, Test.description),
        }[kind]
        query = query.filter(or_(*(field.ilike(term) for field in fields)))
    category_field = {
        "exams": Exam.category,
        "courses": Course.category,
        "current-affairs": CurrentAffair.category,
    }.get(kind)
    if category and category_field is not None:
        query = query.filter(category_field == category)
    type_field = {"opportunities": Opportunity.type, "tests": Test.type}.get(kind)
    if type_filter and type_field is not None:
        query = query.filter(type_field == type_filter)
    return query


@router.get("/queue")
def list_content_queue(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_admin)],
    queue_status: Literal["draft", "pending_review"] = Query("draft", alias="status"),
    page: int = Query(1, ge=1, le=100),
    page_size: int = Query(20, ge=1, le=100),
):
    """List persisted drafts or review submissions; no derived/mock queue rows."""
    rows = []
    counts = 0
    for kind, model in MODELS.items():
        if queue_status == "pending_review" and kind not in {"courses", "current-affairs"}:
            continue
        query = db.query(model).filter(model.status == queue_status)
        counts += query.count()
        rows.extend(
            (item.created_at, kind, item)
            for item in query.order_by(model.created_at.desc(), model.id).limit(page * page_size).all()
        )
    rows.sort(key=lambda row: (row[0].replace(tzinfo=UTC) if row[0].tzinfo is None else row[0], row[2].id), reverse=True)
    page_rows = rows[(page - 1) * page_size : page * page_size]
    items = [
        {
            "kind": kind,
            "id": item.id,
            "slug": item.slug,
            "title": getattr(item, "title", getattr(item, "name", "")),
            "status": item.status.value if hasattr(item.status, "value") else item.status,
            "created_at": created_at,
        }
        for created_at, kind, item in page_rows
    ]
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": counts,
        "total_pages": ceil(counts / page_size) if counts else 0,
    }


@router.get("/{kind}")
def list_admin_content(
    kind: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_admin)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, min_length=1, max_length=100),
    content_status: str | None = Query(None, alias="status"),
    category: str | None = Query(None, min_length=1, max_length=100),
    type_filter: str | None = Query(None, alias="type", min_length=1, max_length=32),
):
    kind = _kind(kind)
    query = _base_query(kind, db, q, category, type_filter)
    if content_status is not None:
        model = MODELS[kind]
        allowed = {
            "exams": {status.value for status in ExamStatus},
            "opportunities": {status.value for status in OpportunityStatus},
            "courses": set(ContentStatus.__args__),
            "current-affairs": set(ContentStatus.__args__),
            "tests": {"draft", "published"},
        }[kind]
        if content_status not in allowed:
            raise HTTPException(status_code=422, detail="invalid status for this content type")
        query = query.filter(model.status == content_status)
    total = query.order_by(None).count()
    model = MODELS[kind]
    records = query.order_by(model.created_at.desc(), model.id).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [_row(kind, item, db) for item in records],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": ceil(total / page_size) if total else 0,
    }


@router.post("/{kind}", status_code=status.HTTP_201_CREATED)
def create_admin_content(
    kind: str,
    payload: dict,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    admin=Depends(require_admin),
):
    kind = _kind(kind)
    schema = _validate_payload(CREATE_SCHEMAS[kind], payload)
    values = schema.model_dump()
    for field in ("official_website", "source_url", "application_url"):
        if values.get(field) is not None:
            values[field] = str(values[field])
    item = MODELS[kind](**values)
    db.add(item)
    try:
        db.flush()
        record_audit(db, action="CREATE", entity=ENTITY_NAMES[kind], entity_id=item.id, actor_id=admin.id, request=request)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="slug already exists") from exc
    db.refresh(item)
    return _row(kind, item, db)


@router.get("/{kind}/{content_id}")
def get_admin_content(
    kind: str,
    content_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_admin)],
):
    kind = _kind(kind)
    return _row(kind, _find(kind, content_id, db), db)


@router.patch("/{kind}/{content_id}")
def update_admin_content(
    kind: str,
    content_id: str,
    payload: dict,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    admin=Depends(require_admin),
):
    kind = _kind(kind)
    schema = _validate_payload(UPDATE_SCHEMAS[kind], payload)
    values = schema.model_dump(exclude_unset=True)
    if kind in {"exams", "opportunities"} and {"status", "verified"}.intersection(values):
        raise HTTPException(status_code=422, detail="Use the content action endpoint to change publication or verification state")
    item = _find(kind, content_id, db)
    for field in ("official_website", "source_url", "application_url"):
        if values.get(field) is not None:
            values[field] = str(values[field])
    for field, value in values.items():
        setattr(item, field, value)
    try:
        record_audit(db, action="UPDATE", entity=ENTITY_NAMES[kind], entity_id=item.id, actor_id=admin.id, request=request)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="slug already exists") from exc
    db.refresh(item)
    return _row(kind, item, db)


@router.post("/{kind}/{content_id}/actions/{action}")
def administer_content_action(
    kind: str,
    content_id: str,
    action: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    admin=Depends(require_admin),
):
    kind = _kind(kind)
    item = _find(kind, content_id, db)
    current = item.status.value if hasattr(item.status, "value") else item.status
    transitions: dict[str, dict[str, str]] = {
        "exams": {"draft:publish": "published", "published:unpublish": "draft", "draft:archive": "archived", "published:archive": "archived", "archived:publish": "published", "draft:verify": "verified", "published:verify": "verified", "archived:verify": "verified", "draft:unverify": "unverified", "published:unverify": "unverified", "archived:unverify": "unverified"},
        "opportunities": {"draft:publish": "published", "closed:publish": "published", "archived:publish": "published", "published:unpublish": "draft", "draft:archive": "archived", "published:archive": "archived", "closed:archive": "archived", "draft:verify": "verified", "published:verify": "verified", "closed:verify": "verified", "archived:verify": "verified", "draft:unverify": "unverified", "published:unverify": "unverified", "closed:unverify": "unverified", "archived:unverify": "unverified", "published:close": "closed"},
        "courses": {"draft:submit": "pending_review", "pending_review:verify": "verified", "pending_review:reject": "rejected", "verified:publish": "published", "published:expire": "expired"},
        "current-affairs": {"draft:review": "pending_review", "pending_review:verify": "verified", "pending_review:reject": "rejected", "verified:publish": "published", "published:expire": "expired"},
        "tests": {"draft:publish": "published", "published:unpublish": "draft"},
    }
    target = transitions[kind].get(f"{current}:{action}")
    if target is None:
        raise HTTPException(status_code=409, detail=f"Cannot {action} {kind} in {current} status")
    if action == "publish" and kind == "tests":
        if not db.query(Question.id).filter(Question.test_id == item.id).first():
            raise HTTPException(status_code=409, detail="test requires at least one question")
    if target in {"published", "verified", "unverified"} and kind in {"exams", "opportunities"}:
        if target == "unverified":
            item.verified = False
            item.verified_at = None
        elif target == "verified":
            item.verified = True
            item.verified_at = datetime.now(UTC)
        else:
            item.status = target
    else:
        item.status = target
    if kind == "current-affairs" and target == "published":
        item.published_at = datetime.now(UTC)
    if kind == "opportunities" and action == "publish":
        item.published_at = datetime.now(UTC)
    elif kind == "opportunities" and action == "unpublish":
        item.published_at = None
    record_audit(db, action=action.upper(), entity=ENTITY_NAMES[kind], entity_id=item.id, actor_id=admin.id, request=request)
    db.commit()
    db.refresh(item)
    return _row(kind, item, db)


@router.post("/tests/{test_id}/questions", status_code=status.HTTP_201_CREATED)
def create_test_question(
    test_id: str,
    payload: QuestionWrite,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    admin=Depends(require_admin),
):
    test = _find("tests", test_id, db)
    if test.status != "draft":
        raise HTTPException(status_code=409, detail="questions can only be changed while a test is a draft")
    if db.query(TestAttempt.id).filter(TestAttempt.test_id == test.id).first():
        raise HTTPException(status_code=409, detail="questions cannot be changed after attempts exist")
    if sum(option.is_correct for option in payload.options) != 1:
        raise HTTPException(status_code=422, detail="exactly one correct option is required")
    question = Question(test_id=test.id, text=payload.text, explanation=payload.explanation, position=payload.position)
    db.add(question)
    db.flush()
    for option in payload.options:
        db.add(QuestionOption(question_id=question.id, **option.model_dump()))
    record_audit(db, action="CREATE_QUESTION", entity="test", entity_id=test.id, actor_id=admin.id, request=request)
    db.commit()
    return {"id": question.id}


@router.put("/tests/{test_id}/questions/{question_id}")
def update_test_question(
    test_id: str,
    question_id: str,
    payload: QuestionWrite,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    admin=Depends(require_admin),
):
    test = _find("tests", test_id, db)
    question = db.query(Question).filter(Question.id == question_id, Question.test_id == test.id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="question not found")
    if test.status != "draft" or db.query(TestAttempt.id).filter(TestAttempt.test_id == test.id).first():
        raise HTTPException(status_code=409, detail="questions can only be changed on a draft test without attempts")
    if sum(option.is_correct for option in payload.options) != 1:
        raise HTTPException(status_code=422, detail="exactly one correct option is required")
    question.text = payload.text
    question.explanation = payload.explanation
    question.position = payload.position
    options = db.query(QuestionOption).filter(QuestionOption.question_id == question.id).order_by(QuestionOption.position, QuestionOption.id).all()
    if len(options) != len(payload.options):
        db.query(QuestionOption).filter(QuestionOption.question_id == question.id).delete(synchronize_session=False)
        db.flush()
        for option in payload.options:
            db.add(QuestionOption(question_id=question.id, **option.model_dump()))
    else:
        for existing, option in zip(options, payload.options, strict=True):
            existing.text = option.text
            existing.position = option.position
            existing.is_correct = option.is_correct
    record_audit(db, action="UPDATE_QUESTION", entity="test", entity_id=test.id, actor_id=admin.id, request=request)
    db.commit()
    return {"id": question.id}


@router.delete("/tests/{test_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_question(
    test_id: str,
    question_id: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    admin=Depends(require_admin),
):
    test = _find("tests", test_id, db)
    question = db.query(Question).filter(Question.id == question_id, Question.test_id == test.id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="question not found")
    if test.status != "draft" or db.query(TestAttempt.id).filter(TestAttempt.test_id == test.id).first():
        raise HTTPException(status_code=409, detail="questions can only be changed on a draft test without attempts")
    record_audit(db, action="DELETE_QUESTION", entity="test", entity_id=test.id, actor_id=admin.id, request=request)
    db.delete(question)
    db.commit()


@router.delete("/{kind}/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_draft_test(
    kind: str,
    content_id: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    admin=Depends(require_admin),
):
    kind = _kind(kind)
    if kind != "tests":
        raise HTTPException(status_code=405, detail="Archive or expire this content instead of deleting it")
    item = _find(kind, content_id, db)
    if item.status != "draft":
        raise HTTPException(status_code=409, detail="only draft tests can be deleted")
    if db.query(TestAttempt.id).filter(TestAttempt.test_id == item.id).first():
        raise HTTPException(status_code=409, detail="tests with attempts cannot be deleted")
    record_audit(db, action="DELETE", entity="test", entity_id=item.id, actor_id=admin.id, request=request)
    db.delete(item)
    db.commit()
