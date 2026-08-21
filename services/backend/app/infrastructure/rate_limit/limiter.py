"""Simple in-memory rate limiting for sensitive auth endpoints."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request, status

from app.core.config import settings

_LIMITS = {
    "login": {"max_requests": 10, "window_seconds": 60},
    "register": {"max_requests": 5, "window_seconds": 60},
    "refresh": {"max_requests": 10, "window_seconds": 60},
    "password_reset": {"max_requests": 5, "window_seconds": 60},
}

_store: dict[str, list[float]] = defaultdict(list)


class _Limiter:
    def limit(self, _key: str):
        def decorator(func: Callable):
            return func

        return decorator


limiter = _Limiter()


def _client_key(request: Request) -> str:
    if request.client is None:
        return "unknown"
    return request.headers.get("x-forwarded-for", request.client.host)


def rate_limit(name: str):
    cfg = _LIMITS[name]

    async def dependency(request: Request) -> None:
        key = f"{name}:{_client_key(request)}"
        now = time.monotonic()
        window_start = now - cfg["window_seconds"]
        requests = _store[key]
        _store[key] = [stamp for stamp in requests if stamp > window_start]
        if len(_store[key]) >= cfg["max_requests"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="rate limit exceeded",
            )
        _store[key].append(now)

    return dependency
