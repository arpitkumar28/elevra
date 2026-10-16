from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.platform import Question, QuestionOption, Test, TestAnswer, TestAttempt
from app.schemas.platform import QuestionWrite, TestWrite
from app.services.audit import record_audit
from app.services.auth import get_current_user, require_admin

router = APIRouter(prefix="/tests", tags=["tests"])


def _public_test(test: Test, db: Session) -> dict:
    questions = db.query(Question).filter(Question.test_id == test.id).order_by(Question.position).all()
    return {"id": test.id, "title": test.title, "slug": test.slug, "description": test.description, "type": test.type, "duration_minutes": test.duration_minutes, "questions": [{"id": q.id, "text": q.text, "position": q.position, "options": [{"id": option.id, "text": option.text, "position": option.position} for option in db.query(QuestionOption).filter(QuestionOption.question_id == q.id).order_by(QuestionOption.position)]} for q in questions]}


@router.get("")
def list_tests(db: Annotated[Session, Depends(get_db)]):
    return [{"id": item.id, "title": item.title, "slug": item.slug, "description": item.description, "type": item.type, "duration_minutes": item.duration_minutes} for item in db.query(Test).filter(Test.status == "published").order_by(Test.created_at.desc()).all()]


@router.get("/{test_id}")
def get_test(test_id: str, db: Annotated[Session, Depends(get_db)]):
    item = db.query(Test).filter(Test.id == test_id, Test.status == "published").first()
    if not item: raise HTTPException(status_code=404, detail="test not found")
    return _public_test(item, db)


@router.post("/{test_id}/start", status_code=status.HTTP_201_CREATED)
def start_test(test_id: str, request: Request, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    test = db.query(Test).filter(Test.id == test_id, Test.status == "published").first()
    if not test: raise HTTPException(status_code=404, detail="test not found")
    active = db.query(TestAttempt).filter(TestAttempt.test_id == test.id, TestAttempt.user_id == user.id, TestAttempt.submitted_at.is_(None)).first()
    if active: return {"attempt_id": active.id, "test": _public_test(test, db), "started_at": active.started_at}
    attempt = TestAttempt(test_id=test.id, user_id=user.id, total_questions=db.query(Question).filter(Question.test_id == test.id).count())
    db.add(attempt); db.flush(); record_audit(db, action="CREATE", entity="test_attempt", entity_id=attempt.id, actor_id=user.id, request=request); db.commit(); return {"attempt_id": attempt.id, "test": _public_test(test, db), "started_at": attempt.started_at}


def _attempt_for(attempt_id: str, user_id: str, db: Session) -> TestAttempt:
    item = db.query(TestAttempt).filter(TestAttempt.id == attempt_id, TestAttempt.user_id == user_id).first()
    if not item: raise HTTPException(status_code=404, detail="attempt not found")
    if item.submitted_at: raise HTTPException(status_code=409, detail="attempt already submitted")
    test = db.get(Test, item.test_id)
    started = item.started_at if item.started_at.tzinfo else item.started_at.replace(tzinfo=UTC)
    if datetime.now(UTC) > started + timedelta(minutes=test.duration_minutes): raise HTTPException(status_code=409, detail="test time has elapsed; submit the attempt")
    return item


@router.put("/attempts/{attempt_id}/answers/{question_id}")
def save_answer(attempt_id: str, question_id: str, payload: dict, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    attempt = _attempt_for(attempt_id, user.id, db)
    question = db.query(Question).filter(Question.id == question_id, Question.test_id == attempt.test_id).first()
    option_id = payload.get("option_id")
    if not question or not option_id or not db.query(QuestionOption.id).filter(QuestionOption.id == option_id, QuestionOption.question_id == question_id).first(): raise HTTPException(status_code=422, detail="invalid answer")
    answer = db.query(TestAnswer).filter(TestAnswer.attempt_id == attempt.id, TestAnswer.question_id == question_id).first()
    if answer: answer.option_id = option_id
    else: db.add(TestAnswer(attempt_id=attempt.id, question_id=question_id, option_id=option_id))
    db.commit(); return {"status": "saved"}


@router.post("/attempts/{attempt_id}/submit")
def submit_attempt(attempt_id: str, request: Request, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    attempt = _attempt_for(attempt_id, user.id, db)
    answers = {answer.question_id: answer.option_id for answer in db.query(TestAnswer).filter(TestAnswer.attempt_id == attempt.id)}
    questions = db.query(Question).filter(Question.test_id == attempt.test_id).all(); correct = 0
    for question in questions:
        selected = answers.get(question.id)
        if selected and db.query(QuestionOption.id).filter(QuestionOption.id == selected, QuestionOption.question_id == question.id, QuestionOption.is_correct.is_(True)).first(): correct += 1
    attempt.score = correct; attempt.submitted_at = datetime.now(UTC); record_audit(db, action="UPDATE", entity="test_attempt", entity_id=attempt.id, actor_id=user.id, request=request, metadata={"result": "submitted"}); db.commit()
    return {"attempt_id": attempt.id, "score": correct, "total_questions": attempt.total_questions, "submitted_at": attempt.submitted_at}


@router.get("/attempts/history")
def attempt_history(db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    return [{"id": item.id, "test_id": item.test_id, "score": item.score, "total_questions": item.total_questions, "started_at": item.started_at, "submitted_at": item.submitted_at} for item in db.query(TestAttempt).filter(TestAttempt.user_id == user.id).order_by(TestAttempt.started_at.desc()).all()]


@router.post("/admin", status_code=status.HTTP_201_CREATED)
def create_test(payload: TestWrite, request: Request, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)):
    if db.query(Test.id).filter(Test.slug == payload.slug).first(): raise HTTPException(status_code=409, detail="slug already exists")
    item = Test(**payload.model_dump()); db.add(item); db.flush(); record_audit(db, action="CREATE", entity="test", entity_id=item.id, actor_id=admin.id, request=request); db.commit(); return {"id": item.id, "status": item.status}


@router.post("/admin/{test_id}/questions", status_code=status.HTTP_201_CREATED)
def add_question(test_id: str, payload: QuestionWrite, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)):
    if not db.get(Test, test_id): raise HTTPException(status_code=404, detail="test not found")
    if sum(1 for option in payload.options if option.is_correct) != 1: raise HTTPException(status_code=422, detail="exactly one correct option is required")
    question = Question(test_id=test_id, text=payload.text, explanation=payload.explanation, position=payload.position); db.add(question); db.flush()
    for option in payload.options: db.add(QuestionOption(question_id=question.id, **option.model_dump()))
    db.commit(); return {"id": question.id}


@router.post("/admin/{test_id}/publish")
def publish_test(test_id: str, db: Annotated[Session, Depends(get_db)], admin=Depends(require_admin)):
    item = db.get(Test, test_id)
    if not item: raise HTTPException(status_code=404, detail="test not found")
    if not db.query(Question.id).filter(Question.test_id == test_id).first(): raise HTTPException(status_code=409, detail="test requires questions")
    item.status = "published"; db.commit(); return {"id": item.id, "status": item.status}
