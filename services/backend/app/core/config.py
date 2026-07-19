"""Runtime settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = Field(default="development", alias="NODE_ENV")
    database_url: str = "postgresql+asyncpg://elevra:elevra@localhost:5432/elevra"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"
    jwt_issuer: str = "elevra"
    jwt_audience: str = "elevra-students"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    ]
    rate_limit_default: str = "120/minute"
    enable_docs: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
