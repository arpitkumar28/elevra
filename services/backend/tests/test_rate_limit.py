from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.infrastructure.rate_limit import limiter


def _request(address: str = "198.51.100.17") -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "scheme": "https",
            "path": "/api/v1/auth/login",
            "raw_path": b"/api/v1/auth/login",
            "query_string": b"",
            "headers": [(b"x-forwarded-for", b"203.0.113.2")],
            "client": (address, 4242),
            "server": ("test", 443),
        }
    )


class FakeRedis:
    def __init__(self, *, fail: bool = False) -> None:
        self.count = 0
        self.fail = fail
        self.calls: list[tuple[str, int, str, int]] = []

    def eval(self, script: str, key_count: int, key: str, ttl: int) -> int:
        if self.fail:
            raise OSError("redis unavailable")
        self.calls.append((script, key_count, key, ttl))
        self.count += 1
        return self.count


def test_production_rate_limit_uses_shared_atomic_redis_counter(monkeypatch):
    redis = FakeRedis()
    monkeypatch.setattr(limiter, "settings", SimpleNamespace(environment="production"))
    monkeypatch.setattr(limiter, "cache_client", SimpleNamespace(client=redis))

    dependency = limiter.rate_limit("login")
    for _ in range(limiter._LIMITS["login"]["max_requests"]):
        asyncio.run(dependency(_request()))

    with pytest.raises(HTTPException) as error:
        asyncio.run(dependency(_request()))

    assert error.value.status_code == 429
    assert len(redis.calls) == limiter._LIMITS["login"]["max_requests"] + 1
    script, key_count, key, ttl = redis.calls[0]
    assert "INCR" in script and "EXPIRE" in script
    assert key_count == 1
    assert "198.51.100.17" not in key
    assert ttl == limiter._LIMITS["login"]["window_seconds"]


def test_production_rate_limit_fails_closed_when_redis_is_unavailable(monkeypatch):
    monkeypatch.setattr(limiter, "settings", SimpleNamespace(environment="production"))
    monkeypatch.setattr(limiter, "cache_client", SimpleNamespace(client=FakeRedis(fail=True)))

    with pytest.raises(HTTPException) as error:
        asyncio.run(limiter.rate_limit("login")(_request()))

    assert error.value.status_code == 503
    assert error.value.detail == "rate limiting temporarily unavailable"
