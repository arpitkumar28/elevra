"""Common pagination, filtering, and sorting query contracts."""

from typing import Annotated, Literal

from fastapi import Query
from pydantic import BaseModel, Field


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort: str = Field(default="created_at")
    direction: Literal["asc", "desc"] = "desc"

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int


def page_params(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    sort: str = "created_at",
    direction: Literal["asc", "desc"] = "desc",
) -> PageParams:
    return PageParams(page=page, page_size=page_size, sort=sort, direction=direction)
