"""应用配置模块：统一从 backend/.env 读取配置。"""

from pathlib import Path

from dotenv import dotenv_values


# backend/.env 位于后端目录；无论从项目根目录或 backend 目录启动都能找到。
BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"
env = dotenv_values(ENV_FILE)


class Settings:
    """集中保存应用运行所需配置。"""

    APP_NAME: str = env.get("APP_NAME", "Learning Site")
    APP_ENV: str = env.get("APP_ENV", "development")
    DATABASE_URL: str = env.get("DATABASE_URL", "sqlite:///./learning.db")
    JWT_SECRET: str = env.get("JWT_SECRET", "")
    JWT_ALGORITHM: str = env.get("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        env.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in env.get("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]

    def validate(self) -> None:
        """启动时检查密钥等关键配置，避免使用空密钥运行。"""
        if not self.JWT_SECRET:
            raise RuntimeError("JWT_SECRET 未配置，请检查 backend/.env")


settings = Settings()
