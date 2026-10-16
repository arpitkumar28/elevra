import importlib

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url


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
