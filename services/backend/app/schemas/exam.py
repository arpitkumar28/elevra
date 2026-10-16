from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, HttpUrl, constr, field_validator
from typing import Optional

Slug = constr(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", min_length=3, max_length=255)
SearchQuery = constr(strip_whitespace=True, min_length=1, max_length=100)


class PublicationStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class ExamBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=2, max_length=255)
    slug: Slug
    short_description: Optional[constr(strip_whitespace=True, max_length=512)] = None
    description: Optional[str] = None
    category: "ExamCategory"
    conducting_body: Optional[constr(strip_whitespace=True, max_length=255)] = None
    official_website: Optional[HttpUrl] = None
    source_url: Optional[HttpUrl] = None
    source_name: Optional[str] = None


class ExamCreate(ExamBase):
    application_start: Optional[date] = None
    application_deadline: Optional[date] = None
    exam_date: Optional[date] = None
    result_date: Optional[date] = None


class ExamUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=2, max_length=255)] = None
    slug: Optional[Slug] = None
    short_description: Optional[constr(strip_whitespace=True, max_length=512)] = None
    description: Optional[str] = None
    category: Optional["ExamCategory"] = None
    conducting_body: Optional[constr(strip_whitespace=True, max_length=255)] = None
    official_website: Optional[HttpUrl] = None
    source_url: Optional[HttpUrl] = None
    source_name: Optional[str] = None
    status: Optional[PublicationStatus] = None
    verified: Optional[bool] = None
    application_start: Optional[date] = None
    application_deadline: Optional[date] = None
    exam_date: Optional[date] = None
    result_date: Optional[date] = None

    @field_validator("name", "slug", "category", mode="before")
    @classmethod
    def required_fields_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("value cannot be null")
        return value


class ExamResponse(ExamBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: PublicationStatus
    verified: bool
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

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


class ExamPage(BaseModel):
    items: list[ExamResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
