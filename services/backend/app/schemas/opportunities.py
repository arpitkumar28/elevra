"""Opportunity API contracts shared by web, mobile, and public API clients."""

from app.domain.models.enums import OpportunityStatus, OpportunityType
from pydantic import BaseModel, Field, HttpUrl


class OpportunitySearchParams(BaseModel):
    query: str | None = None
    type: OpportunityType | None = None
    country: str | None = None
    grade_level: str | None = None
    tags: list[str] = Field(default_factory=list)


class OpportunityRead(BaseModel):
    id: str
    type: OpportunityType
    status: OpportunityStatus
    title: str
    provider_name: str
    description: str
    country: str | None = None
    grade_levels: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    source_url: HttpUrl | None = None
    deadline_at: str | None = None
    popularity_score: float = 0


class OpportunityCreate(BaseModel):
    type: OpportunityType
    title: str = Field(min_length=3, max_length=320)
    provider_name: str = Field(min_length=2, max_length=240)
    description: str = Field(min_length=20)
    country: str | None = Field(default=None, max_length=80)
    grade_levels: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list, max_length=20)
    source_url: HttpUrl | None = None
    deadline_at: str | None = None
