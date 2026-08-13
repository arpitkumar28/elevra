import uuid
from enum import Enum
from sqlalchemy import String, Text, DateTime, Boolean, Enum as SAEnum, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.session import Base


class OpportunityType(str, Enum):
    job = "job"
    internship = "internship"
    scholarship = "scholarship"
    hackathon = "hackathon"
    competition = "competition"
    fellowship = "fellowship"
    research = "research"
    bootcamp = "bootcamp"
    event = "event"
    other = "other"


class OpportunityStatus(str, Enum):
    draft = "draft"
    published = "published"
    closed = "closed"
    archived = "archived"


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    type: Mapped[OpportunityType] = mapped_column(SAEnum(OpportunityType, name="opportunity_type"), nullable=False, index=True)
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    eligibility: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    remote: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    application_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    deadline: Mapped[Date | None] = mapped_column(Date, nullable=True, index=True)
    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[OpportunityStatus] = mapped_column(SAEnum(OpportunityStatus, name="opportunity_status"), nullable=False, default=OpportunityStatus.draft, index=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    verified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
