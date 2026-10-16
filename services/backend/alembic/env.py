from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.db.session import Base
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.exam import Exam
from app.models.exam_syllabus import ExamSyllabus
from app.models.exam_pattern import ExamPattern
from app.models.exam_dates import ExamDate
from app.models.exam_faq import ExamFAQ
from app.models.opportunity import Opportunity
from app.models.platform import Application, AuditLog, Bookmark, Course, CurrentAffair, Notification, Question, QuestionOption, Test, TestAnswer, TestAttempt

config = context.config
config.set_main_option("sqlalchemy.url", settings.alembic_database_url)
if config.config_file_name is not None and config.file_config.has_section("formatters"):
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
