"""所有接口可复用的基础响应模型。"""

from typing import Any

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """通用消息响应。"""

    message: str


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str
    app_name: str


class DetailResponse(BaseModel):
    """可携带附加数据的通用响应。"""

    detail: str
    data: Any | None = None
