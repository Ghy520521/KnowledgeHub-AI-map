"""数据库模型统一导出。"""

from app.models.user import User
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.study_record import StudyRecord

__all__ = ["User", "Course", "Lesson", "StudyRecord"]
