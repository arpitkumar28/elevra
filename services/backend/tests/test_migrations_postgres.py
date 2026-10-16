"""Opt-in PostgreSQL/pgvector smoke test for the full Alembic upgrade.

Run only against the empty database from docker-compose.migration-test.yml.
The strict URL checks intentionally reject remote and non-test databases.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from app.db.session import Base
from app.models import (  # noqa: F401
    account_token,
    exam,
    exam_dates,
    exam_faq,
    exam_pattern,
    exam_syllabus,
    opportunity,
    platform,
    refresh_token,
    student_profile,
    user,
)
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import make_url
from sqlalchemy.types import Enum as SqlEnum

BACKEND_ROOT = Path(__file__).resolve().parents[1]
TEST_URL_ENV = "ELEVRA_MIGRATION_TEST_DATABASE_URL"


def _test_database_url() -> str:
    value = os.getenv(TEST_URL_ENV)
    if not value:
        pytest.fail(f"{TEST_URL_ENV} is required; refusing to skip the PostgreSQL migration test")

    url = make_url(value)
    if (
        not url.drivername.startswith("postgresql")
        or url.host not in {"localhost", "127.0.0.1", "::1"}
        or url.database != "elevra_migration_test"
    ):
        pytest.fail(
            f"{TEST_URL_ENV} must target local PostgreSQL database elevra_migration_test; "
            "the URL value is suppressed"
        )
    return value


def _type_signature(column_type, dialect) -> tuple[str, tuple[str, ...] | None]:
    if isinstance(column_type, SqlEnum):
        return column_type.name or "", tuple(column_type.enums)
    return column_type.compile(dialect=dialect), None


def _redact_database_urls(output: str, database_url: str) -> str:
    output = output.replace(database_url, "<redacted disposable database URL>")
    return re.sub(
        r"(?i)(postgres(?:ql)?(?:\+\w+)?://[^:/\s]+:)[^@/\s]+@",
        r"\1<redacted>@",
        output,
    )


@pytest.mark.integration
def test_fresh_postgres_pgvector_upgrade_matches_active_orm() -> None:
    database_url = _test_database_url()
    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        assert (
            inspector.get_table_names(schema="public") == []
        ), "migration integration database must be empty before upgrade"

        env = os.environ.copy()
        env["DATABASE_URL"] = database_url
        env["ALEMBIC_DATABASE_URL"] = database_url
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=BACKEND_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (
            "Alembic upgrade head failed against the disposable database "
            f"(exit {result.returncode}). Sanitized output follows:\n"
            f"{_redact_database_urls(result.stdout + result.stderr, database_url)}"
        )

        inspector = inspect(engine)
        actual_tables = set(inspector.get_table_names(schema="public"))
        expected_tables = set(Base.metadata.tables)
        assert expected_tables <= actual_tables

        dialect = postgresql.dialect()
        for table_name, model_table in Base.metadata.tables.items():
            actual_columns = {
                column["name"]: column
                for column in inspector.get_columns(
                    table_name,
                    schema="public",
                )
            }
            assert set(model_table.columns.keys()) <= actual_columns.keys(), table_name

            for model_column in model_table.columns:
                actual_column = actual_columns[model_column.name]
                assert actual_column["nullable"] == model_column.nullable, (
                    table_name,
                    model_column.name,
                )
                assert _type_signature(actual_column["type"], dialect) == _type_signature(
                    model_column.type, dialect
                ), (
                    table_name,
                    model_column.name,
                )
                if model_column.server_default is not None:
                    assert actual_column["default"] is not None, (table_name, model_column.name)

            actual_fks = {
                (
                    tuple(fk["constrained_columns"]),
                    fk["referred_table"],
                    tuple(fk["referred_columns"]),
                    (fk.get("options") or {}).get("ondelete", "").upper(),
                )
                for fk in inspector.get_foreign_keys(table_name, schema="public")
            }
            expected_fks = {
                (
                    tuple(element.parent.name for element in constraint.elements),
                    constraint.elements[0].column.table.name,
                    tuple(element.column.name for element in constraint.elements),
                    (constraint.ondelete or "").upper(),
                )
                for constraint in model_table.foreign_key_constraints
            }
            assert expected_fks <= actual_fks, table_name

            actual_indexes = {
                (tuple(index["column_names"]), bool(index["unique"]))
                for index in inspector.get_indexes(table_name, schema="public")
            }
            expected_indexes = {
                (tuple(column.name for column in index.columns), bool(index.unique))
                for index in model_table.indexes
            }
            assert expected_indexes <= actual_indexes, table_name

            actual_unique_constraints = {
                tuple(constraint["column_names"])
                for constraint in inspector.get_unique_constraints(table_name, schema="public")
            }
            actual_unique_constraints.update(
                columns for columns, unique in actual_indexes if unique
            )
            expected_unique_constraints = {
                tuple(column.name for column in constraint.columns)
                for constraint in model_table.constraints
                if constraint.__class__.__name__ == "UniqueConstraint"
            }
            expected_unique_constraints.update(
                tuple(column.name for column in index.columns)
                for index in model_table.indexes
                if index.unique
            )
            assert expected_unique_constraints <= actual_unique_constraints, table_name

        with engine.connect() as connection:
            assert (
                connection.execute(
                    text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                ).scalar_one_or_none()
                == 1
            )
            revisions = (
                connection.execute(text("SELECT version_num FROM public.alembic_version"))
                .scalars()
                .all()
            )
        assert revisions == ["20260821_core_platform_domains"]
    finally:
        engine.dispose()
