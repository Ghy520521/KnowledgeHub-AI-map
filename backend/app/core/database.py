"""SQLAlchemy 数据库连接、会话及模型基类。"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


# SQLite 在单线程之外需要关闭同线程限制，以便 FastAPI 可正常使用连接。
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """所有数据库模型都继承此基类。"""


def get_db() -> Generator[Session, None, None]:
    """FastAPI 数据库会话依赖：请求结束后关闭会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
