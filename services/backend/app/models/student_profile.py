import uuid
from datetime import date
from sqlalchemy import Boolean, Date, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    state: Mapped[str | None] = mapped_column(String(128), nullable=True)
    country: Mapped[str | None] = mapped_column(String(128), nullable=True)
    education_level: Mapped[str | None] = mapped_column(String(128), nullable=True)
    institution: Mapped[str | None] = mapped_column(String(255), nullable=True)
    degree: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stream: Mapped[str | None] = mapped_column(String(255), nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(nullable=True)
    exam_interests: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    opportunity_interests: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_locations: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    remote_preference: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    career_interests: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    target_roles: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    experience_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notification_preferences: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    user: Mapped["User"] = relationship(back_populates="profile")
