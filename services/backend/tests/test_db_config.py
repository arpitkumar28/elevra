import importlib

import pytest
from sqlalchemy import create_engine
from alembic.config import Config
from sqlalchemy.engine import make_url

from app.db.alembic_config import escape_alembic_config_value


def test_alembic_config_accepts_percent_encoded_database_credentials():
    database_url = (
        "postgresql+psycopg://postgres:p%40ss%2Fword"
        "@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres?sslmode=require"
    )

    config = Config()
    config.set_main_option("sqlalchemy.url", escape_alembic_config_value(database_url))

    restored_url = config.get_main_option("sqlalchemy.url")
    assert restored_url == database_url
    assert make_url(restored_url).password == "p@ss/word"


@pytest.mark.parametrize(
    "url",
    [
        "postgres://user:password@db.example:5432/elevra",
        "postgresql://user:password@db.example:5432/elevra",
        "postgresql+psycopg2://user:password@db.example:5432/elevra",
    ],
)
def test_sync_postgres_urls_select_psycopg3(url):
    from app.core.config import _normalize_sync_database_url

    normalized = _normalize_sync_database_url(url)
    assert make_url(normalized).drivername == "postgresql+psycopg"


def test_render_main_defaults_to_production_when_environment_is_missing(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.delenv("RENDER_GIT_BRANCH", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.setenv("APP_ENV", "development")

    from app.core.config import Settings, _resolve_environment

    assert _resolve_environment() == "production"
    assert Settings().environment == "production"


def test_render_develop_branch_defaults_to_staging(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("RENDER_GIT_BRANCH", "develop")
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.setenv("APP_ENV", "production")

    from app.core.config import Settings, _resolve_environment

    assert _resolve_environment() == "staging"
    assert Settings().environment == "staging"


@pytest.mark.parametrize(
    ("branch", "expected"),
    [("main", "production"), ("develop", "staging")],
)
def test_render_never_uses_development_mode(monkeypatch, branch, expected):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("RENDER_GIT_BRANCH", branch)
    monkeypatch.setenv("ENVIRONMENT", "development")

    from app.core.config import _resolve_environment

    assert _resolve_environment() == expected


def test_explicit_render_environment_is_respected(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("APP_ENV", "development")

    from app.core.config import Settings

    assert Settings().environment == "staging"


def test_render_database_and_alembic_urls_load_psycopg3(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:password@db.example:5432/elevra")
    monkeypatch.setenv("ALEMBIC_DATABASE_URL", "postgres://user:password@db.example:5432/elevra")

    from app.core.config import Settings

    settings = Settings()
    for url in (settings.database_url, settings.alembic_database_url):
        engine = create_engine(url)
        try:
            assert engine.dialect.driver == "psycopg"
            assert engine.dialect.dbapi.__name__ == "psycopg"
        finally:
            engine.dispose()


def test_supabase_database_configuration(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SUPABASE_DB_HOST", "db.example.supabase.co")
    monkeypatch.setenv("SUPABASE_DB_NAME", "postgres")
    monkeypatch.setenv("SUPABASE_DB_USER", "postgres")
    monkeypatch.setenv("SUPABASE_DB_PASSWORD", "secret-password")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL_ASYNC", raising=False)
    monkeypatch.delenv("ALEMBIC_DATABASE_URL", raising=False)

    import app.core.config as config_module

    importlib.reload(config_module)

    settings = config_module.settings
    assert settings.database_url == "postgresql+psycopg://postgres:secret-password@db.example.supabase.co:5432/postgres?sslmode=require"
    assert settings.database_url_async == "postgresql+asyncpg://postgres:secret-password@db.example.supabase.co:5432/postgres?ssl=require"
    assert settings.alembic_database_url == settings.database_url
