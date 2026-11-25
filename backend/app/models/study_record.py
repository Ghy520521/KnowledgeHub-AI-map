"""学习进度数据库模型。"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StudyRecord(Base):
    """学习进度表：记录学员对课程课时的已学习状态。"""

    __tablename__ = "study_record"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_study_record_user_lesson"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id", ondelete="CASCADE"), nullable=False)
    learned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    studied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="study_records")
    lesson: Mapped["Lesson"] = relationship(back_populates="study_records")
