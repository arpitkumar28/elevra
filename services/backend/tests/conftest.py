import sys
import os
from collections.abc import Generator
from pathlib import Path

# Allow the repository-root command requested for this milestone to discover
# the backend application without relying on the development database.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("USE_SQLITE_FOR_TESTS", "true")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.models.exam import Exam  # noqa: F401
from app.models.exam_dates import ExamDate  # noqa: F401
from app.models.exam_faq import ExamFAQ  # noqa: F401
from app.models.exam_pattern import ExamPattern  # noqa: F401
from app.models.exam_syllabus import ExamSyllabus  # noqa: F401
from app.models.opportunity import Opportunity  # noqa: F401
from app.models.student_profile import StudentProfile  # noqa: F401
from app.models.user import User
from app.models.platform import Application, AuditLog, Bookmark, Course, CurrentAffair, Notification, Question, QuestionOption, Test, TestAnswer, TestAttempt  # noqa: F401
from app.services.auth import create_access_token


@pytest.fixture(autouse=True)
def clear_rate_limit_state():
    from app.infrastructure.rate_limit.limiter import _store

    _store.clear()


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_headers(db: Session) -> dict[str, str]:
    user = User(name="Admin", email="admin@example.com", password_hash="unused", is_admin=True)
    db.add(user)
    db.commit()
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


@pytest.fixture()
def student_headers(db: Session) -> dict[str, str]:
    user = User(name="Student", email="student@example.com", password_hash="unused", is_admin=False)
    db.add(user)
    db.commit()
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}
