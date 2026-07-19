"""Shared response contracts for all clients."""

from typing import Generic, TypeVar

from app.core.pagination import PageMeta
from pydantic import BaseModel

T = TypeVar("T")


class ApiEnvelope(BaseModel, Generic[T]):
    data: T
    request_id: str


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PageMeta
    request_id: str
