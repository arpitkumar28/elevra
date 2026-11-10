"""Create the initial student schema without duplicating the legacy users table.

The legacy root already creates users for its RBAC tables. This revision is
therefore conditional for users and creates only the student profile table
when absent. Later revisions reconcile both tables to the active ORM.
"""
from alembic import op
import sqlalchemy as sa


revision = "20260812_initial_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names(schema="public"))

    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )

    user_indexes = {
        index["name"]
        for index in sa.inspect(bind).get_indexes("users", schema="public")
    }
    if "ix_users_email" not in user_indexes:
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    if "student_profiles" not in tables:
        op.create_table(
            "student_profiles",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("goal", sa.Text(), nullable=True),
            sa.Column("bio", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    profile_indexes = {
        index["name"]
        for index in sa.inspect(bind).get_indexes("student_profiles", schema="public")
    }
    if "ix_student_profiles_user_id" not in profile_indexes:
        op.create_index(
            "ix_student_profiles_user_id",
            "student_profiles",
            ["user_id"],
            unique=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names(schema="public"))

    if "student_profiles" in tables:
        indexes = {
            index["name"]
            for index in inspector.get_indexes("student_profiles", schema="public")
        }
        if "ix_student_profiles_user_id" in indexes:
            op.drop_index("ix_student_profiles_user_id", table_name="student_profiles")
        op.drop_table("student_profiles")

    # users may predate this revision (the legacy root creates it), so only
    # remove the email index here when it was created by this revision. The
    # table itself is intentionally retained for the legacy root and RBAC data.
