"""Simple in-memory rate limiting for sensitive auth endpoints."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request, status

from app.core.config import settings

def _parse_limit(value: str) -> dict[str, int]:
    count, separator, period = value.partition("/")
    if not separator or not count.isdigit() or int(count) < 1:
        raise ValueError(f"Invalid rate limit: {value}")
    windows = {"second": 1, "minute": 60, "hour": 3600}
    if period not in windows:
        raise ValueError(f"Invalid rate limit period: {value}")
    return {"max_requests": int(count), "window_seconds": windows[period]}


_LIMITS = {
    "login": _parse_limit(settings.rate_limit_login),
    "register": _parse_limit(settings.rate_limit_register),
    "refresh": _parse_limit(settings.rate_limit_refresh),
    "password_reset": _parse_limit(settings.rate_limit_password_reset),
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
    # Never accept a caller-controlled forwarding header as the rate-limit identity.
    return request.client.host


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
