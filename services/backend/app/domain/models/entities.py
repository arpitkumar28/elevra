"""Production data model for the Elevra platform."""

from app.domain.models.enums import (
    AuditAction,
    NotificationChannel,
    OpportunityStatus,
    OpportunityType,
)
from app.infrastructure.database.base import Base, TimestampMixin, UuidPrimaryKeyMixin
from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(240), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(512))
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    graduation_year: Mapped[int | None] = mapped_column(Integer)
    locale: Mapped[str] = mapped_column(String(16), default="en", nullable=False)
    timezone: Mapped[str] = mapped_column(String(80), default="UTC", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    roles: Mapped[list["Role"]] = relationship(secondary="user_roles", back_populates="users")


class Role(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    users: Mapped[list[User]] = relationship(secondary="user_roles", back_populates="roles")
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permissions", back_populates="roles"
    )


class Permission(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "permissions"

    key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    roles: Mapped[list[Role]] = relationship(
        secondary="role_permissions",
        back_populates="permissions",
    )


class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[str] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )


class Organization(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(240), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(2048))
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Opportunity(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "opportunities"
    __table_args__ = (
        Index("ix_opportunities_type_status_deadline", "type", "status", "deadline_at"),
        Index("ix_opportunities_search_vector", "title", "provider_name"),
    )

    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"))
    type: Mapped[OpportunityType] = mapped_column(String(40), nullable=False)
    status: Mapped[OpportunityStatus] = mapped_column(
        String(40), default=OpportunityStatus.PENDING_REVIEW, nullable=False
    )
    title: Mapped[str] = mapped_column(String(320), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str | None] = mapped_column(String(80))
    grade_levels: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048))
    deadline_at: Mapped[str | None] = mapped_column(String(40))
    popularity_score: Mapped[float] = mapped_column(Numeric(8, 4), default=0, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Course(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(String(320), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(40), nullable=False)


class Lesson(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lessons"

    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(320), nullable=False)
    content_url: Mapped[str | None] = mapped_column(String(2048))
    position: Mapped[int] = mapped_column(Integer, nullable=False)


class Note(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notes"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[str | None] = mapped_column(ForeignKey("lessons.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)


class MockTest(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "mock_tests"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    exam_key: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    score_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    analytics_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Bookmark(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "opportunity_id",
            name="uq_bookmark_user_opportunity",
        ),
    )

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    opportunity_id: Mapped[str] = mapped_column(
        ForeignKey("opportunities.id", ondelete="CASCADE"), index=True
    )


class Notification(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    channel: Mapped[NotificationChannel] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class AiChat(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_chats"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    agent_key: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    messages_json: Mapped[list[dict]] = mapped_column(JSONB, default=list, nullable=False)


class StudyPlan(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "study_plans"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    target_exam: Mapped[str | None] = mapped_column(String(120))
    tasks_json: Mapped[list[dict]] = mapped_column(JSONB, default=list, nullable=False)


class Application(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "applications"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id"), index=True)
    status: Mapped[str] = mapped_column(String(80), default="draft", nullable=False)
    checklist_json: Mapped[list[dict]] = mapped_column(JSONB, default=list, nullable=False)


class AuditLog(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[AuditAction] = mapped_column(String(40), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(120), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(80))
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class UserSetting(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "settings"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(120), nullable=False)
    value_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class AnalyticsEvent(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "analytics_events"

    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    event_name: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(80), nullable=False)
    properties_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
