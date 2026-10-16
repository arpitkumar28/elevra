import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _build_database_url(
    driver: str,
    *,
    host: str,
    port: int,
    db_name: str,
    username: str,
    password: str,
    ssl_mode: str = "require",
) -> str:
    encoded_password = password.replace("@", "%40")
    if driver == "psycopg":
        return f"postgresql+psycopg://{username}:{encoded_password}@{host}:{port}/{db_name}?sslmode={ssl_mode}"
    if driver == "asyncpg":
        return f"postgresql+asyncpg://{username}:{encoded_password}@{host}:{port}/{db_name}?ssl={ssl_mode}"
    raise ValueError(f"Unsupported database driver: {driver}")


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "elevra")
    # ENVIRONMENT is the deployment contract; APP_ENV remains a backwards-
    # compatible local alias.
    environment: str = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development")).lower()
    supabase_db_host: str = os.getenv("SUPABASE_DB_HOST", "localhost")
    supabase_db_port: int = int(os.getenv("SUPABASE_DB_PORT", "5432"))
    supabase_db_name: str = os.getenv("SUPABASE_DB_NAME", "elevra")
    supabase_db_user: str = os.getenv("SUPABASE_DB_USER", "elevra")
    supabase_db_password: str = os.getenv("SUPABASE_DB_PASSWORD", "elevra_dev_password")
    supabase_sslmode: str = os.getenv("SUPABASE_SSLMODE", "require")
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL")
        or _build_database_url(
            "psycopg",
            host=os.getenv("SUPABASE_DB_HOST", "localhost"),
            port=int(os.getenv("SUPABASE_DB_PORT", "5432")),
            db_name=os.getenv("SUPABASE_DB_NAME", "elevra"),
            username=os.getenv("SUPABASE_DB_USER", "elevra"),
            password=os.getenv("SUPABASE_DB_PASSWORD", "elevra_dev_password"),
            ssl_mode=os.getenv("SUPABASE_SSLMODE", "require"),
        )
    )
    database_url_async: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL_ASYNC")
        or _build_database_url(
            "asyncpg",
            host=os.getenv("SUPABASE_DB_HOST", "localhost"),
            port=int(os.getenv("SUPABASE_DB_PORT", "5432")),
            db_name=os.getenv("SUPABASE_DB_NAME", "elevra"),
            username=os.getenv("SUPABASE_DB_USER", "elevra"),
            password=os.getenv("SUPABASE_DB_PASSWORD", "elevra_dev_password"),
            ssl_mode=os.getenv("SUPABASE_SSLMODE", "require"),
        )
    )
    alembic_database_url: str = field(
        default_factory=lambda: os.getenv("ALEMBIC_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or _build_database_url(
            "psycopg",
            host=os.getenv("SUPABASE_DB_HOST", "localhost"),
            port=int(os.getenv("SUPABASE_DB_PORT", "5432")),
            db_name=os.getenv("SUPABASE_DB_NAME", "elevra"),
            username=os.getenv("SUPABASE_DB_USER", "elevra"),
            password=os.getenv("SUPABASE_DB_PASSWORD", "elevra_dev_password"),
            ssl_mode=os.getenv("SUPABASE_SSLMODE", "require"),
        )
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
    rate_limit_login: str = os.getenv("RATE_LIMIT_LOGIN", "10/minute")
    rate_limit_register: str = os.getenv("RATE_LIMIT_REGISTER", "5/minute")
    rate_limit_refresh: str = os.getenv("RATE_LIMIT_REFRESH", "10/minute")
    rate_limit_password_reset: str = os.getenv("RATE_LIMIT_PASSWORD_RESET", "5/minute")
    allowed_origins: List[str] = field(
        default_factory=lambda: [
            origin.strip().rstrip("/")
            for origin in os.getenv(
                "CORS_ORIGINS",
                os.getenv(
                    "ALLOWED_ORIGINS",
                    "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001",
                ),
            ).split(",")
            if origin.strip()
        ]
    )


def validate_security_settings(config: Settings) -> None:
    """Fail closed when deployment would sign tokens with the development key."""
    if config.environment not in {"development", "test"} and (
        config.jwt_secret.strip().lower() in {"", "change-me", "secret", "your-secret-key"}
        or len(config.jwt_secret) < 32
    ):
        raise RuntimeError("JWT_SECRET must be a non-placeholder value of at least 32 characters outside development")


settings = Settings()
