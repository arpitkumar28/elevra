"""Add explicit remote, hybrid, and on-site opportunity modes."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20261111_opportunity_work_mode"
down_revision: str | None = "20261111_opportunity_workflow"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("opportunities", sa.Column("work_mode", sa.String(length=16), nullable=True))
    # Preserve the only unambiguous legacy value. remote=False did not
    # distinguish hybrid from on-site, so keep those records unspecified.
    op.execute(
        "UPDATE opportunities SET work_mode = 'remote' "
        "WHERE remote IS TRUE AND work_mode IS NULL"
    )
    op.create_check_constraint(
        "ck_opportunities_work_mode",
        "opportunities",
        "work_mode IS NULL OR work_mode IN ('remote', 'hybrid', 'on_site')",
    )
    op.create_index("ix_opportunities_work_mode", "opportunities", ["work_mode"])


def downgrade() -> None:
    raise RuntimeError(
        "20261111_opportunity_work_mode is forward-only; downgrading would discard hybrid/on-site classifications"
    )
