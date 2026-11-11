"""Add a controlled opportunity lifecycle and student application history."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20261111_opportunity_workflow"
down_revision: str | None = "20261110_enable_public_rls"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Preserve the original labels and append the workflow states. This is a
    # forward-only extension of the existing PostgreSQL enum type.
    op.execute("ALTER TYPE opportunity_status ADD VALUE IF NOT EXISTS 'pending_review'")
    op.execute("ALTER TYPE opportunity_status ADD VALUE IF NOT EXISTS 'verified'")
    op.execute("ALTER TYPE opportunity_status ADD VALUE IF NOT EXISTS 'rejected'")

    op.add_column("opportunities", sa.Column("summary", sa.String(length=512), nullable=True))
    op.add_column("opportunities", sa.Column("application_start", sa.Date(), nullable=True))
    op.add_column("opportunities", sa.Column("source_name", sa.String(length=255), nullable=True))
    op.add_column("opportunities", sa.Column("source_checked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("opportunities", sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("opportunities", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("opportunities", sa.Column("reviewed_by_id", sa.String(length=36), nullable=True))
    op.add_column("opportunities", sa.Column("review_note", sa.Text(), nullable=True))
    op.add_column("opportunities", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        "fk_opportunities_reviewed_by_users",
        "opportunities",
        "users",
        ["reviewed_by_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_opportunities_submitted_at", "opportunities", ["submitted_at"])
    op.create_index("ix_opportunities_status_deadline", "opportunities", ["status", "deadline"])

    op.add_column("applications", sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("applications", sa.Column("follow_up_date", sa.Date(), nullable=True))

    # Refuse to add referential/uniqueness guarantees if legacy tracker data
    # already violates them. Operators must resolve these rows explicitly.
    connection = op.get_bind()
    duplicate = connection.execute(
        sa.text(
            """
            SELECT user_id, opportunity_id
            FROM applications
            WHERE opportunity_id IS NOT NULL
            GROUP BY user_id, opportunity_id
            HAVING COUNT(*) > 1
            LIMIT 1
            """
        )
    ).first()
    if duplicate:
        raise RuntimeError(
            "Cannot add the application uniqueness index: duplicate student/opportunity tracker rows exist"
        )

    orphan = connection.execute(
        sa.text(
            """
            SELECT applications.id
            FROM applications
            LEFT JOIN opportunities ON opportunities.id = applications.opportunity_id
            WHERE applications.opportunity_id IS NOT NULL
              AND opportunities.id IS NULL
            LIMIT 1
            """
        )
    ).first()
    if orphan:
        raise RuntimeError(
            "Cannot add the opportunity foreign key: application tracker rows reference missing opportunities"
        )

    op.create_foreign_key(
        "fk_applications_opportunity_id_opportunities",
        "applications",
        "opportunities",
        ["opportunity_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "uq_applications_user_opportunity",
        "applications",
        ["user_id", "opportunity_id"],
        unique=True,
        postgresql_where=sa.text("opportunity_id IS NOT NULL"),
    )

    op.create_table(
        "application_events",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "application_id",
            sa.String(length=36),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("previous_status", sa.String(length=32), nullable=True),
        sa.Column("new_status", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_application_events_application_id", "application_events", ["application_id"])
    op.create_index("ix_application_events_user_id", "application_events", ["user_id"])
    op.create_index(
        "ix_application_events_application_created_at",
        "application_events",
        ["application_id", "created_at"],
    )

    # The RLS baseline has already been applied to existing public tables.
    # Enable it explicitly for this newly-created table too.
    op.execute("ALTER TABLE public.application_events ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    raise RuntimeError(
        "20261111_opportunity_workflow is forward-only; use a reviewed forward fix or approved backup recovery"
    )
