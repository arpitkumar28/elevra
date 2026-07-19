"""Crawler job contracts."""

from pydantic import BaseModel, Field, HttpUrl


class CrawlRequest(BaseModel):
    source_url: HttpUrl
    source_type: str = Field(pattern="^(scholarship|internship|competition|course|exam)$")
    priority: int = Field(default=5, ge=1, le=10)


class CrawlJob(BaseModel):
    id: str
    status: str
    source_url: HttpUrl
    priority: int
