"""FastAPI 应用入口：中间件、数据库初始化和基础接口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.users import router as users_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import (
    http_exception_handler,
    sqlalchemy_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.models import Course, Lesson, StudyRecord, User  # noqa: F401


@asynccontextmanager
async def lifespan(application: FastAPI):
    """应用启动时校验配置并自动创建尚不存在的数据库表。"""
    settings.validate()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="学习网站 MVP 后端 API",
    version="0.1.0",
    lifespan=lifespan,
)

# 配置前端跨域来源，具体白名单由 backend/.env 控制。
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 为HTTP错误、参数校验、数据库错误和未知异常注册统一处理器。
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# 挂载用户模块路由；后续课程等模块可沿用相同方式接入。
app.include_router(users_router)


@app.get("/", tags=["基础"])
def read_root() -> dict[str, str]:
    """根路径接口，确认后端服务已启动。"""
    return {"message": "学习网站后端运行成功"}


@app.get("/health", tags=["基础"])
def health_check() -> dict[str, str]:
    """健康检查接口，用于启动验证和部署探活。"""
    return {"status": "ok", "app_name": settings.APP_NAME}
