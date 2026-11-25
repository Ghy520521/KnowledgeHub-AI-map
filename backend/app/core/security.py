"""密码哈希和 JWT 令牌生成、解析。"""

from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """使用随机盐和 PBKDF2-SHA256 对密码进行不可逆哈希。"""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), 600_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """校验明文密码是否与数据库中的哈希一致。"""
    try:
        algorithm, salt, expected = password_hash.split("$", 2)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("ascii"), 600_000
        ).hex()
        return secrets.compare_digest(actual, expected)
    except (ValueError, UnicodeError):
        return False


def create_access_token(subject: str) -> str:
    """为用户生成带过期时间的 JWT access token。"""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    """解析 JWT，并返回令牌中的用户标识；解析失败抛出 JWTError。"""
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise JWTError("令牌缺少有效的用户标识")
    return subject
