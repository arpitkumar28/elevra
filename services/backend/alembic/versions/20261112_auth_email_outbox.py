"""Add a private, retryable outbox for account-security emails.

Revision ID: 20261112_auth_email_outbox
Revises: 20261111_opportunity_work_mode
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20261112_auth_email_outbox"
down_revision: str | None = "20261111_opportunity_work_mode"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "email_outbox",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "account_token_id",
            sa.String(length=36),
            sa.ForeignKey("account_tokens.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("recipient_email", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("encrypted_token", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), server_default="pending", nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("max_attempts", sa.Integer(), server_default="5", nullable=False),
        sa.Column(
            "next_attempt_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("last_error", sa.String(length=128), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'retry', 'sent', 'failed')",
            name="ck_email_outbox_status",
        ),
        sa.CheckConstraint("attempt_count >= 0", name="ck_email_outbox_attempt_count"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_token_id", name="uq_email_outbox_account_token_id"),
    )
    op.create_index(
        "ix_email_outbox_status_next_attempt",
        "email_outbox",
        ["status", "next_attempt_at"],
    )
    op.create_index("ix_email_outbox_locked_until", "email_outbox", ["locked_until"])
    # This table contains recipient addresses and encrypted one-time credentials.
    # It is intentionally inaccessible to browser roles and only used by the API
    # service's server-side database connection.
    op.execute("ALTER TABLE public.email_outbox ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    raise RuntimeError(
        "20261112_auth_email_outbox is forward-only; do not drop queued or sent account-security email records"
    )
