"""Simple in-memory rate limiting for sensitive auth endpoints."""

from __future__ import annotations

import time
from collections import defaultdict
from hashlib import sha256
from typing import Callable

from fastapi import HTTPException, Request, status

from app.core.config import settings
from app.infrastructure.cache import cache_client

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

_INCREMENT_WITH_TTL = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""


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
        client_key = _client_key(request)
        if settings.environment not in {"development", "test"}:
            # Redis gives all application workers one atomic counter per client
            # and window. Hash the address so rate-limit keys do not retain IPs.
            key_digest = sha256(client_key.encode("utf-8")).hexdigest()
            redis_key = f"elevra:rate-limit:{name}:{key_digest}"
            try:
                count = int(
                    cache_client.client.eval(
                        _INCREMENT_WITH_TTL,
                        1,
                        redis_key,
                        cfg["window_seconds"],
                    )
                )
            except Exception as exc:
                # A deployment must not silently drop its authentication rate
                # limits when the shared store is unavailable.
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="rate limiting temporarily unavailable",
                ) from exc
            if count > cfg["max_requests"]:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="rate limit exceeded",
                )
            return

        key = f"{name}:{client_key}"
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
