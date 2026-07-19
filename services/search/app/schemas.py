"""Search service request and response contracts."""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=160)
    filters: dict[str, str | list[str]] = Field(default_factory=dict)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SearchHit(BaseModel):
    id: str
    title: str
    type: str
    provider: str
    score: float


class SearchResponse(BaseModel):
    hits: list[SearchHit]
    estimated_total_hits: int
    processing_time_ms: int
