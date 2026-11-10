"""Enable RLS on every application table in the exposed public schema.

Revision ID: 20261110_enable_public_rls
Revises: 20261110_align_active_orm
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20261110_enable_public_rls"
down_revision: str | None = "20261110_align_active_orm"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    preparer = bind.dialect.identifier_preparer
    tables = sa.inspect(bind).get_table_names(schema="public")

    for table_name in tables:
        # Alembic's own revision ledger is operational metadata, not an app
        # table exposed to clients.
        if table_name == "alembic_version":
            continue
        quoted_name = preparer.quote(table_name)
        op.execute(sa.text(f"ALTER TABLE public.{quoted_name} ENABLE ROW LEVEL SECURITY"))


def downgrade() -> None:
    # Keep public tables deny-by-default if the application is rolled back.
    raise RuntimeError(
        "20261110_enable_public_rls is forward-only; do not disable row-level security during rollback"
    )
