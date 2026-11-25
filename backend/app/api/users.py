"""用户注册、登录、个人信息及修改密码接口。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse
from app.schemas.user import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


router = APIRouter(prefix="/api", tags=["用户模块"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> User:
    """注册普通学员账号，并校验用户名和邮箱是否重复。"""
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已被注册")

    user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(request.password),
        role=UserRole.STUDENT,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        # 并发注册时数据库唯一约束可能先于查询触发，必须回滚并转换为友好错误。
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名或邮箱已存在")
    return user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """验证用户名或邮箱与密码，成功后返回JWT访问令牌。"""
    account = request.username.strip()
    user = db.query(User).filter(
        or_(User.username == account, User.email == account.lower())
    ).first()

    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.get("/users/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """获取当前登录用户信息，不需要传入用户ID。"""
    return current_user


@router.put("/users/password", response_model=MessageResponse)
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """校验旧密码后修改当前登录用户密码。"""
    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确")
    if request.old_password == request.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码不能与旧密码相同")

    current_user.password_hash = hash_password(request.new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return MessageResponse(message="密码修改成功")
