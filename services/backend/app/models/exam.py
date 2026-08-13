import uuid
from enum import Enum
from sqlalchemy import String, Text, Date, DateTime, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.session import Base


class ExamCategory(str, Enum):
    government = "government"
    engineering = "engineering"
    medical = "medical"
    management = "management"
    university = "university"
    defence = "defence"
    banking = "banking"
    railway = "railway"
    teaching = "teaching"
    state_exams = "state_exams"
    other = "other"


class PublicationStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    short_description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[ExamCategory] = mapped_column(SAEnum(ExamCategory, name="exam_category"), nullable=False, index=True)
    conducting_body: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    official_website: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    eligibility_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    education_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    age_limit: Mapped[str | None] = mapped_column(String(255), nullable=True)
    application_start: Mapped[Date | None] = mapped_column(Date, nullable=True)
    application_deadline: Mapped[Date | None] = mapped_column(Date, nullable=True, index=True)
    exam_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    result_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    status: Mapped[PublicationStatus] = mapped_column(SAEnum(PublicationStatus, name="publication_status"), nullable=False, default=PublicationStatus.draft, index=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    verified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
