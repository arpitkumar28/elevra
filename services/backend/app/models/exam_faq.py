import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ExamFAQ(Base):
    __tablename__ = "exam_faqs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id: Mapped[str] = mapped_column(String(255), ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    question: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
