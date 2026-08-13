from alembic import op

revision = "20260813_enable_pgvector"
down_revision = "20260812_add_exams_opportunities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
