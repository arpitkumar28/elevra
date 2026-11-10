from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, constr, field_validator


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
    pending_review = "pending_review"
    verified = "verified"
    rejected = "rejected"


class OpportunityBase(BaseModel):
    title: constr(strip_whitespace=True, min_length=2, max_length=255)
    slug: constr(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", min_length=3, max_length=255)
    type: OpportunityType
    organization: Optional[constr(strip_whitespace=True, max_length=255)] = None
    summary: Optional[constr(strip_whitespace=True, max_length=512)] = None
    description: Optional[str] = None
    eligibility: Optional[str] = None
    location: Optional[constr(strip_whitespace=True, max_length=255)] = None
    remote: bool = False
    application_start: Optional[date] = None
    application_url: Optional[HttpUrl] = None
    source_name: Optional[constr(strip_whitespace=True, max_length=255)] = None
    source_url: Optional[HttpUrl] = None


class OpportunityCreate(OpportunityBase):
    deadline: Optional[date] = None


class OpportunityUpdate(BaseModel):
    title: Optional[constr(strip_whitespace=True, min_length=2, max_length=255)] = None
    slug: Optional[constr(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", min_length=3, max_length=255)] = None
    type: Optional[OpportunityType] = None
    organization: Optional[constr(strip_whitespace=True, max_length=255)] = None
    summary: Optional[constr(strip_whitespace=True, max_length=512)] = None
    description: Optional[str] = None
    eligibility: Optional[str] = None
    location: Optional[constr(strip_whitespace=True, max_length=255)] = None
    remote: Optional[bool] = None
    application_start: Optional[date] = None
    application_url: Optional[HttpUrl] = None
    source_name: Optional[constr(strip_whitespace=True, max_length=255)] = None
    source_url: Optional[HttpUrl] = None
    deadline: Optional[date] = None

    @field_validator("title", "slug", "type", mode="before")
    @classmethod
    def required_fields_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("value cannot be null")
        return value


class OpportunityResponse(OpportunityBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    deadline: Optional[date] = None
    published_at: Optional[datetime] = None
    status: OpportunityStatus
    verified: bool
    verified_at: Optional[datetime] = None
    source_checked_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by_id: Optional[str] = None
    review_note: Optional[str] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class OpportunityPage(BaseModel):
    items: list[OpportunityResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
