from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, HttpUrl, constr
from typing import Optional


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


class OpportunityBase(BaseModel):
    title: constr(strip_whitespace=True, min_length=2, max_length=255)
    slug: constr(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", min_length=3, max_length=255)
    type: OpportunityType
    organization: Optional[constr(strip_whitespace=True, max_length=255)] = None
    description: Optional[str] = None
    eligibility: Optional[str] = None
    location: Optional[constr(strip_whitespace=True, max_length=255)] = None
    remote: Optional[bool] = False
    application_url: Optional[HttpUrl] = None
    source_url: Optional[HttpUrl] = None


class OpportunityCreate(OpportunityBase):
    deadline: Optional[date] = None


class OpportunityUpdate(BaseModel):
    title: Optional[constr(strip_whitespace=True, min_length=2, max_length=255)] = None
    description: Optional[str] = None
    eligibility: Optional[str] = None
    location: Optional[constr(strip_whitespace=True, max_length=255)] = None
    remote: Optional[bool] = None
    deadline: Optional[date] = None
    status: Optional[OpportunityStatus] = None
    verified: Optional[bool] = None


class OpportunityResponse(OpportunityBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    deadline: Optional[date] = None
    published_at: Optional[datetime] = None
    status: OpportunityStatus
    verified: bool
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class OpportunityPage(BaseModel):
    items: list[OpportunityResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
