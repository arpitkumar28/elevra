from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ContentStatus = Literal["draft", "pending_review", "verified", "published", "rejected", "expired"]
TestType = Literal["mock", "practice", "topic", "previous_year"]
BookmarkType = Literal["exam", "job", "internship", "scholarship", "course", "competition", "current_affair"]
ApplicationStatus = Literal["saved", "applied", "in_progress", "interview", "selected", "rejected", "withdrawn"]


class CourseWrite(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    provider: str = Field(min_length=2, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, max_length=100)
    difficulty: str | None = Field(default=None, max_length=50)
    duration: str | None = Field(default=None, max_length=100)
    mode: str | None = Field(default=None, max_length=50)
    skills: list[str] = Field(default_factory=list, max_length=30)
    certificate: bool = False
    course_url: str | None = Field(default=None, max_length=2048)
    official_url: str | None = Field(default=None, max_length=2048)


class CourseUpdate(CourseWrite):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    provider: str | None = Field(default=None, min_length=2, max_length=255)

    @field_validator("title", "slug", "provider", mode="before")
    @classmethod
    def required_course_fields_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("value cannot be null")
        return value


class CourseRead(CourseWrite):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: ContentStatus
    created_at: datetime
    updated_at: datetime


class CurrentAffairWrite(BaseModel):
    title: str = Field(min_length=2, max_length=320)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    summary: str = Field(min_length=10)
    content: str = Field(min_length=20)
    category: str = Field(min_length=2, max_length=100)
    source: str = Field(min_length=2, max_length=255)
    source_url: str | None = Field(default=None, max_length=2048)


class CurrentAffairUpdate(CurrentAffairWrite):
    title: str | None = Field(default=None, min_length=2, max_length=320)
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    summary: str | None = Field(default=None, min_length=10)
    content: str | None = Field(default=None, min_length=20)
    category: str | None = Field(default=None, min_length=2, max_length=100)
    source: str | None = Field(default=None, min_length=2, max_length=255)

    @field_validator("title", "slug", "summary", "content", "category", "source", mode="before")
    @classmethod
    def required_affair_fields_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("value cannot be null")
        return value


class CurrentAffairRead(CurrentAffairWrite):
    model_config = ConfigDict(from_attributes=True)
    id: str
    published_at: datetime | None
    status: ContentStatus
    created_at: datetime
    updated_at: datetime


class TestWrite(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = None
    type: TestType
    duration_minutes: int = Field(ge=1, le=600)


class TestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = None
    type: TestType | None = None
    duration_minutes: int | None = Field(default=None, ge=1, le=600)

    @field_validator("title", "slug", "type", "duration_minutes", mode="before")
    @classmethod
    def required_test_fields_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("value cannot be null")
        return value


class TestAdminRead(BaseModel):
    id: str
    title: str
    slug: str
    description: str | None = None
    type: TestType
    duration_minutes: int
    status: Literal["draft", "published"]
    created_at: datetime
    updated_at: datetime
    questions: list[dict] = Field(default_factory=list)


class QuestionOptionWrite(BaseModel):
    text: str = Field(min_length=1)
    is_correct: bool = False
    position: int = Field(default=0, ge=0)


class QuestionWrite(BaseModel):
    text: str = Field(min_length=1)
    explanation: str | None = None
    position: int = Field(default=0, ge=0)
    options: list[QuestionOptionWrite] = Field(min_length=2)


class BookmarkWrite(BaseModel):
    entity_type: BookmarkType
    entity_id: str = Field(min_length=1, max_length=36)


class ApplicationWrite(BaseModel):
    opportunity_id: str | None = Field(default=None, max_length=36)
    title: str = Field(min_length=2, max_length=255)
    organization: str | None = Field(default=None, max_length=255)
    external_url: str | None = Field(default=None, max_length=2048)
    status: ApplicationStatus = "saved"
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    opportunity_id: str | None = Field(default=None, max_length=36)
    title: str | None = Field(default=None, min_length=2, max_length=255)
    organization: str | None = Field(default=None, max_length=255)
    external_url: str | None = Field(default=None, max_length=2048)
    status: ApplicationStatus | None = None
    notes: str | None = None

    @field_validator("title", "status", mode="before")
    @classmethod
    def required_values_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("value cannot be null")
        return value
