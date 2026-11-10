"""Complete the fresh-install schema to match active SQLAlchemy metadata.

This forward-only revision adds missing user/profile attributes, token tables,
and the indexes omitted by earlier hand-written revisions. It intentionally
does not drop or rename application data.
"""
from alembic import op
import sqlalchemy as sa

revision = "20261110_align_active_orm"
down_revision = "20260821_core_platform_domains"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> dict[str, dict]:
    return {
        column["name"]: column
        for column in sa.inspect(op.get_bind()).get_columns(table_name, schema="public")
    }


def _ensure_column(table_name: str, column: sa.Column) -> None:
    if column.name not in _columns(table_name):
        op.add_column(table_name, column)


def _ensure_index(
    table_name: str,
    index_name: str,
    columns: list[str],
    *,
    unique: bool = False,
) -> None:
    indexes = {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes(table_name, schema="public")
    }
    if index_name not in indexes:
        op.create_index(index_name, table_name, columns, unique=unique)


def upgrade() -> None:
    bind = op.get_bind()

    # The current User model has a narrower contract than the earliest legacy
    # users table. Missing fields are added without dropping legacy columns.
    user_columns = _columns("users")
    if "name" not in user_columns:
        op.add_column("users", sa.Column("name", sa.String(255), nullable=True))
        if "full_name" in user_columns:
            op.execute(
                "UPDATE users SET name = COALESCE(NULLIF(full_name, ''), "
                "NULLIF(split_part(email, '@', 1), ''), 'Student') WHERE name IS NULL"
            )
        else:
            op.execute(
                "UPDATE users SET name = COALESCE(NULLIF(split_part(email, '@', 1), ''), "
                "'Student') WHERE name IS NULL"
            )
        op.alter_column("users", "name", existing_type=sa.String(255), nullable=False)

    user_columns = _columns("users")
    if "is_admin" not in user_columns:
        op.add_column(
            "users",
            sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
    user_columns = _columns("users")
    if "is_active" not in user_columns:
        op.add_column(
            "users",
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
    user_columns = _columns("users")
    if "role" not in user_columns:
        op.add_column(
            "users",
            sa.Column("role", sa.String(32), nullable=False, server_default="student"),
        )
    user_columns = _columns("users")
    if "email_verified" not in user_columns:
        op.add_column(
            "users",
            sa.Column("email_verified", sa.Boolean(), nullable=True),
        )
        if "is_verified" in user_columns:
            op.execute("UPDATE users SET email_verified = COALESCE(is_verified, false)")
        else:
            op.execute("UPDATE users SET email_verified = false WHERE email_verified IS NULL")
        op.alter_column(
            "users",
            "email_verified",
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        )
    user_columns = _columns("users")
    if "locked_until" not in user_columns:
        op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))
    user_columns = _columns("users")
    if "created_at" not in user_columns:
        op.add_column(
            "users",
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
    else:
        op.alter_column(
            "users",
            "created_at",
            existing_type=user_columns["created_at"]["type"],
            server_default=sa.func.now(),
        )
    _ensure_index("users", "ix_users_email", ["email"], unique=True)
    _ensure_index("users", "ix_users_role", ["role"])

    # Complete student_profiles while retaining goal and bio data.
    profile_columns = _columns("student_profiles")
    profile_additions = [
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(64), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("city", sa.String(128), nullable=True),
        sa.Column("state", sa.String(128), nullable=True),
        sa.Column("country", sa.String(128), nullable=True),
        sa.Column("education_level", sa.String(128), nullable=True),
        sa.Column("institution", sa.String(255), nullable=True),
        sa.Column("degree", sa.String(255), nullable=True),
        sa.Column("stream", sa.String(255), nullable=True),
        sa.Column("graduation_year", sa.Integer(), nullable=True),
        sa.Column("exam_interests", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("opportunity_interests", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("preferred_locations", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("remote_preference", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("career_interests", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("target_roles", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("skills", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("experience_level", sa.String(64), nullable=True),
        sa.Column("notification_preferences", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    ]
    for column in profile_additions:
        if column.name not in profile_columns:
            op.add_column("student_profiles", column)
    _ensure_index("student_profiles", "ix_student_profiles_user_id", ["user_id"], unique=True)

    # Persisted token records required by the custom JWT refresh and account
    # recovery flows.
    if not sa.inspect(bind).has_table("account_tokens", schema="public"):
        op.create_table(
            "account_tokens",
            sa.Column("id", sa.String(36), primary_key=True, nullable=False),
            sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("purpose", sa.String(32), nullable=False),
            sa.Column("token_hash", sa.String(64), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("token_hash", name="uq_account_tokens_token_hash"),
        )
    _ensure_index("account_tokens", "ix_account_tokens_user_id", ["user_id"])
    _ensure_index("account_tokens", "ix_account_tokens_purpose", ["purpose"])

    if not sa.inspect(bind).has_table("refresh_tokens", schema="public"):
        op.create_table(
            "refresh_tokens",
            sa.Column("id", sa.String(36), primary_key=True, nullable=False),
            sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("token_hash", sa.String(128), nullable=False),
            sa.Column("session_id", sa.String(64), nullable=True),
            sa.Column("user_agent", sa.String(512), nullable=True),
            sa.Column("ip_address", sa.String(64), nullable=True),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("replaced_by", sa.String(36), nullable=True),
            sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
        )
    _ensure_index("refresh_tokens", "ix_refresh_tokens_user_id", ["user_id"])
    _ensure_index("refresh_tokens", "ix_refresh_tokens_token_hash", ["token_hash"], unique=True)
    _ensure_index("refresh_tokens", "ix_refresh_tokens_session_id", ["session_id"])

    # Complete ORM indexes for the content and student workflow models.
    index_specs = [
        ("exams", "ix_exams_conducting_body", ["conducting_body"], False),
        ("exams", "ix_exams_application_deadline", ["application_deadline"], False),
        ("courses", "ix_courses_title", ["title"], False),
        ("courses", "ix_courses_slug", ["slug"], True),
        ("courses", "ix_courses_provider", ["provider"], False),
        ("courses", "ix_courses_category", ["category"], False),
        ("courses", "ix_courses_difficulty", ["difficulty"], False),
        ("courses", "ix_courses_mode", ["mode"], False),
        ("courses", "ix_courses_status", ["status"], False),
        ("current_affairs", "ix_current_affairs_title", ["title"], False),
        ("current_affairs", "ix_current_affairs_slug", ["slug"], True),
        ("current_affairs", "ix_current_affairs_category", ["category"], False),
        ("current_affairs", "ix_current_affairs_published_at", ["published_at"], False),
        ("current_affairs", "ix_current_affairs_status", ["status"], False),
        ("tests", "ix_tests_title", ["title"], False),
        ("tests", "ix_tests_slug", ["slug"], True),
        ("tests", "ix_tests_type", ["type"], False),
        ("tests", "ix_tests_status", ["status"], False),
        ("questions", "ix_questions_test_id", ["test_id"], False),
        ("question_options", "ix_question_options_question_id", ["question_id"], False),
        ("test_attempts", "ix_test_attempts_test_id", ["test_id"], False),
        ("test_attempts", "ix_test_attempts_user_id", ["user_id"], False),
        ("test_answers", "ix_test_answers_attempt_id", ["attempt_id"], False),
        ("test_answers", "ix_test_answers_question_id", ["question_id"], False),
        ("bookmarks", "ix_bookmarks_user_id", ["user_id"], False),
        ("bookmarks", "ix_bookmarks_entity_type", ["entity_type"], False),
        ("bookmarks", "ix_bookmarks_entity_id", ["entity_id"], False),
        ("applications", "ix_applications_user_id", ["user_id"], False),
        ("applications", "ix_applications_opportunity_id", ["opportunity_id"], False),
        ("applications", "ix_applications_status", ["status"], False),
        ("notifications", "ix_notifications_user_id", ["user_id"], False),
        ("notifications", "ix_notifications_type", ["type"], False),
        ("audit_logs", "ix_audit_logs_actor_id", ["actor_id"], False),
        ("audit_logs", "ix_audit_logs_action", ["action"], False),
        ("audit_logs", "ix_audit_logs_entity", ["entity"], False),
        ("audit_logs", "ix_audit_logs_entity_id", ["entity_id"], False),
        ("audit_logs", "ix_audit_logs_request_id", ["request_id"], False),
    ]
    for table_name, index_name, columns, unique in index_specs:
        _ensure_index(table_name, index_name, columns, unique=unique)


def downgrade() -> None:
    # This revision is deliberately forward-only: account/session records and
    # user profile fields may contain live user data. Use an approved backup
    # restore/recovery plan instead of a destructive downgrade.
    raise RuntimeError(
        "20261110_align_active_orm is forward-only; restore from an approved backup "
        "or apply a reviewed forward fix"
    )
