"""全局异常处理器：统一 API 错误响应格式。"""

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """处理 HTTPException，使业务错误返回统一结构。"""
    del request
    headers = getattr(exc, "headers", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": "HTTP_ERROR"},
        headers=headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理请求体、路径参数和查询参数校验错误。"""
    del request
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(include_url=False),
            "code": "VALIDATION_ERROR",
        },
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """处理数据库异常，并向客户端隐藏内部SQL和字段信息。"""
    del request
    del exc
    return JSONResponse(
        status_code=500,
        content={"detail": "数据库操作失败，请稍后重试", "code": "DATABASE_ERROR"},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """兜底处理未预期异常，避免泄露服务端堆栈。"""
    del request
    del exc
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试", "code": "INTERNAL_ERROR"},
    )
