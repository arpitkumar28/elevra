import redis

from app.core.config import settings


class CacheClient:
    def __init__(self, url: str | None = None) -> None:
        self.client = redis.from_url(url or settings.redis_url, decode_responses=True)

    def ping(self) -> bool:
        try:
            return bool(self.client.ping())
        except Exception:
            return False

    def get(self, key: str) -> str | None:
        return self.client.get(key)

    def set(self, key: str, value: str, ttl: int = 60) -> None:
        self.client.set(key, value, ex=ttl)

    def ttl(self, key: str) -> int:
        return int(self.client.ttl(key))

    def close(self) -> None:
        try:
            self.client.close()
        except Exception:
            # Redis is an optional runtime dependency for public reads; a
            # shutdown failure must not prevent the API from stopping.
            pass


cache_client = CacheClient()


def check_redis() -> bool:
    return cache_client.ping()
