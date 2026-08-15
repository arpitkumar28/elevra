import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "elevra")
    environment: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://elevra:elevra_dev_password@localhost:5432/elevra",
    )
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    db_connect_timeout: int = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_issuer: str = os.getenv("JWT_ISSUER", "elevra")
    jwt_audience: str = os.getenv("JWT_AUDIENCE", "elevra-students")
    access_token_ttl_seconds: int = int(os.getenv("ACCESS_TOKEN_TTL_SECONDS", "900"))
    refresh_token_ttl_seconds: int = int(os.getenv("REFRESH_TOKEN_TTL_SECONDS", "604800"))
    rate_limit_default: str = os.getenv("RATE_LIMIT_DEFAULT", "20/minute")
    allowed_origins: List[str] = field(
        default_factory=lambda: os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001",
        ).split(",")
    )


settings = Settings()
