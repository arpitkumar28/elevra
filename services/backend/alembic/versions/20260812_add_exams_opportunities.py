from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260812_add_exams_opportunities"
down_revision = "20260812_initial_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The existing authentication model uses this role flag. Keep it in this
    # additive migration so already-created user tables are not replaced.
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    # enums
    exam_category = postgresql.ENUM(
        "government",
        "engineering",
        "medical",
        "management",
        "university",
        "defence",
        "banking",
        "railway",
        "teaching",
        "state_exams",
        "other",
        name="exam_category", create_type=False,
    )
    exam_category.create(op.get_bind(), checkfirst=True)

    publication_status = postgresql.ENUM("draft", "published", "archived", name="publication_status", create_type=False)
    publication_status.create(op.get_bind(), checkfirst=True)

    opportunity_type = postgresql.ENUM(
        "job",
        "internship",
        "scholarship",
        "hackathon",
        "competition",
        "fellowship",
        "research",
        "bootcamp",
        "event",
        "other",
        name="opportunity_type", create_type=False,
    )
    opportunity_type.create(op.get_bind(), checkfirst=True)

    opportunity_status = postgresql.ENUM("draft", "published", "closed", "archived", name="opportunity_status", create_type=False)
    opportunity_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "exams",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("short_description", sa.String(length=512), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", exam_category, nullable=False),
        sa.Column("conducting_body", sa.String(length=255), nullable=True),
        sa.Column("official_website", sa.String(length=1024), nullable=True),
        sa.Column("eligibility_summary", sa.Text(), nullable=True),
        sa.Column("education_requirements", sa.Text(), nullable=True),
        sa.Column("age_limit", sa.String(length=255), nullable=True),
        sa.Column("application_start", sa.Date(), nullable=True),
        sa.Column("application_deadline", sa.Date(), nullable=True),
        sa.Column("exam_date", sa.Date(), nullable=True),
        sa.Column("result_date", sa.Date(), nullable=True),
        sa.Column("status", publication_status, nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exams_slug"), "exams", ["slug"], unique=True)
    op.create_index(op.f("ix_exams_name"), "exams", ["name"], unique=False)
    op.create_index(op.f("ix_exams_category"), "exams", ["category"], unique=False)
    op.create_index(op.f("ix_exams_status"), "exams", ["status"], unique=False)
    op.create_index(op.f("ix_exams_verified"), "exams", ["verified"], unique=False)

    # exam content
    op.create_table(
        "exam_syllabi",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("exam_id", sa.String(length=255), nullable=False),
        sa.Column("section_title", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exam_syllabi_exam_id"), "exam_syllabi", ["exam_id"], unique=False)

    op.create_table(
        "exam_patterns",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("exam_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exam_patterns_exam_id"), "exam_patterns", ["exam_id"], unique=False)

    op.create_table(
        "exam_dates",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("exam_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("date", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exam_dates_exam_id"), "exam_dates", ["exam_id"], unique=False)

    op.create_table(
        "exam_faqs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("exam_id", sa.String(length=255), nullable=False),
        sa.Column("question", sa.String(length=1024), nullable=True),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exam_faqs_exam_id"), "exam_faqs", ["exam_id"], unique=False)

    # opportunities
    op.create_table(
        "opportunities",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("type", opportunity_type, nullable=False),
        sa.Column("organization", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("eligibility", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("remote", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("application_url", sa.String(length=1024), nullable=True),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", opportunity_status, nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_opportunities_slug"), "opportunities", ["slug"], unique=True)
    op.create_index(op.f("ix_opportunities_title"), "opportunities", ["title"], unique=False)
    op.create_index(op.f("ix_opportunities_type"), "opportunities", ["type"], unique=False)
    op.create_index(op.f("ix_opportunities_organization"), "opportunities", ["organization"], unique=False)
    op.create_index(op.f("ix_opportunities_location"), "opportunities", ["location"], unique=False)
    op.create_index(op.f("ix_opportunities_remote"), "opportunities", ["remote"], unique=False)
    op.create_index(op.f("ix_opportunities_deadline"), "opportunities", ["deadline"], unique=False)
    op.create_index(op.f("ix_opportunities_status"), "opportunities", ["status"], unique=False)
    op.create_index(op.f("ix_opportunities_verified"), "opportunities", ["verified"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_opportunities_verified"), table_name="opportunities")
    op.drop_index(op.f("ix_opportunities_status"), table_name="opportunities")
    op.drop_index(op.f("ix_opportunities_deadline"), table_name="opportunities")
    op.drop_index(op.f("ix_opportunities_type"), table_name="opportunities")
    op.drop_index(op.f("ix_opportunities_title"), table_name="opportunities")
    op.drop_index(op.f("ix_opportunities_organization"), table_name="opportunities")
    op.drop_index(op.f("ix_opportunities_location"), table_name="opportunities")
    op.drop_index(op.f("ix_opportunities_remote"), table_name="opportunities")
    op.drop_index(op.f("ix_opportunities_slug"), table_name="opportunities")
    op.drop_table("opportunities")

    op.drop_index(op.f("ix_exam_faqs_exam_id"), table_name="exam_faqs")
    op.drop_table("exam_faqs")
    op.drop_index(op.f("ix_exam_dates_exam_id"), table_name="exam_dates")
    op.drop_table("exam_dates")
    op.drop_index(op.f("ix_exam_patterns_exam_id"), table_name="exam_patterns")
    op.drop_table("exam_patterns")
    op.drop_index(op.f("ix_exam_syllabi_exam_id"), table_name="exam_syllabi")
    op.drop_table("exam_syllabi")

    op.drop_index(op.f("ix_exams_verified"), table_name="exams")
    op.drop_index(op.f("ix_exams_status"), table_name="exams")
    op.drop_index(op.f("ix_exams_category"), table_name="exams")
    op.drop_index(op.f("ix_exams_name"), table_name="exams")
    op.drop_index(op.f("ix_exams_slug"), table_name="exams")
    op.drop_table("exams")

    # drop enums
    sa.Enum(name="opportunity_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="opportunity_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="publication_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="exam_category").drop(op.get_bind(), checkfirst=True)
    op.drop_column("users", "is_admin")
