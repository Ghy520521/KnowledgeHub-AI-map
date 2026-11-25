"""用户模块的请求和响应数据模型。"""

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    """用户注册请求。"""

    username: str = Field(min_length=3, max_length=50, description="用户名，长度为3到50个字符")
    email: str = Field(max_length=255, description="登录邮箱")
    password: str = Field(min_length=8, max_length=128, description="密码，长度至少为8个字符")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """清理并校验用户名只包含字母、数字或常用连接符。"""
        value = value.strip()
        if not value:
            raise ValueError("用户名不能为空")
        if not all(character.isalnum() or character in "_-" for character in value):
            raise ValueError("用户名只能包含字母、数字、下划线或连字符")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """进行基础邮箱格式校验并统一转为小写。"""
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("邮箱格式不正确")
        local, separator, domain = value.rpartition("@")
        if not separator or not local or "." not in domain:
            raise ValueError("邮箱格式不正确")
        return value


class LoginRequest(BaseModel):
    """用户登录请求。登录账号支持用户名。"""

    username: str = Field(min_length=1, max_length=50, description="用户名")
    password: str = Field(min_length=1, max_length=128, description="密码")


class ChangePasswordRequest(BaseModel):
    """修改密码请求。"""

    old_password: str = Field(min_length=1, max_length=128, description="当前旧密码")
    new_password: str = Field(min_length=8, max_length=128, description="新密码，长度至少为8个字符")


class UserResponse(BaseModel):
    """用户公开信息响应，不返回密码哈希。"""

    id: int
    username: str
    email: str
    role: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT访问令牌响应。"""

    access_token: str
    token_type: str = "bearer"
