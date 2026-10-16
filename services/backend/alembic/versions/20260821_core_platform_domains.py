"""Add core platform content, student workflow, test, and audit domains.

Revision ID: 20260821_core_platform_domains
Revises: 20260821_merge_deployment_heads
Create Date: 2026-08-21
"""

from alembic import op
import sqlalchemy as sa

revision = "20260821_core_platform_domains"
down_revision = "20260821_merge_deployment_heads"
branch_labels = None
depends_on = None


def _id_column():
    return sa.Column("id", sa.String(length=36), primary_key=True)


def upgrade() -> None:
    op.create_table("courses", _id_column(), sa.Column("title", sa.String(255), nullable=False), sa.Column("slug", sa.String(255), nullable=False, unique=True), sa.Column("provider", sa.String(255), nullable=False), sa.Column("description", sa.Text()), sa.Column("category", sa.String(100)), sa.Column("difficulty", sa.String(50)), sa.Column("duration", sa.String(100)), sa.Column("mode", sa.String(50)), sa.Column("skills", sa.JSON(), nullable=False), sa.Column("certificate", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("course_url", sa.String(2048)), sa.Column("official_url", sa.String(2048)), sa.Column("status", sa.String(32), nullable=False, server_default="draft"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("current_affairs", _id_column(), sa.Column("title", sa.String(320), nullable=False), sa.Column("slug", sa.String(255), nullable=False, unique=True), sa.Column("summary", sa.Text(), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("category", sa.String(100), nullable=False), sa.Column("source", sa.String(255), nullable=False), sa.Column("source_url", sa.String(2048)), sa.Column("published_at", sa.DateTime(timezone=True)), sa.Column("status", sa.String(32), nullable=False, server_default="draft"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("tests", _id_column(), sa.Column("title", sa.String(255), nullable=False), sa.Column("slug", sa.String(255), nullable=False, unique=True), sa.Column("description", sa.Text()), sa.Column("type", sa.String(32), nullable=False), sa.Column("duration_minutes", sa.Integer(), nullable=False), sa.Column("status", sa.String(32), nullable=False, server_default="draft"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("questions", _id_column(), sa.Column("test_id", sa.String(36), sa.ForeignKey("tests.id", ondelete="CASCADE"), nullable=False), sa.Column("text", sa.Text(), nullable=False), sa.Column("explanation", sa.Text()), sa.Column("position", sa.Integer(), nullable=False, server_default="0"))
    op.create_table("question_options", _id_column(), sa.Column("question_id", sa.String(36), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False), sa.Column("text", sa.Text(), nullable=False), sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("position", sa.Integer(), nullable=False, server_default="0"))
    op.create_table("test_attempts", _id_column(), sa.Column("test_id", sa.String(36), sa.ForeignKey("tests.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True), nullable=False), sa.Column("submitted_at", sa.DateTime(timezone=True)), sa.Column("score", sa.Integer()), sa.Column("total_questions", sa.Integer(), nullable=False, server_default="0"))
    op.create_table("test_answers", _id_column(), sa.Column("attempt_id", sa.String(36), sa.ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False), sa.Column("question_id", sa.String(36), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False), sa.Column("option_id", sa.String(36), sa.ForeignKey("question_options.id", ondelete="SET NULL")), sa.UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question"))
    op.create_table("bookmarks", _id_column(), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("entity_type", sa.String(32), nullable=False), sa.Column("entity_id", sa.String(36), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("user_id", "entity_type", "entity_id", name="uq_bookmark_user_entity"))
    op.create_table("applications", _id_column(), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("opportunity_id", sa.String(36)), sa.Column("title", sa.String(255), nullable=False), sa.Column("organization", sa.String(255)), sa.Column("external_url", sa.String(2048)), sa.Column("status", sa.String(32), nullable=False, server_default="saved"), sa.Column("notes", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("notifications", _id_column(), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("type", sa.String(64), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("read_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("audit_logs", _id_column(), sa.Column("actor_id", sa.String(36)), sa.Column("action", sa.String(64), nullable=False), sa.Column("entity", sa.String(64), nullable=False), sa.Column("entity_id", sa.String(36)), sa.Column("request_id", sa.String(64)), sa.Column("metadata_json", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    for table in ("audit_logs", "notifications", "applications", "bookmarks", "test_answers", "test_attempts", "question_options", "questions", "tests", "current_affairs", "courses"):
        op.drop_table(table)
