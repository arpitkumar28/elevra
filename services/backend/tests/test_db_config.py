import importlib


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
