"""应用配置

使用 pydantic-settings 从环境变量读取配置。
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置项，所有值从环境变量读取"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用
    APP_NAME: str = "CrazyMail"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # 服务器
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # 邮件 API
    EMAIL_API_PROVIDER: str = "mail.tm"
    EMAIL_API_BASE_URL: str = "https://api.mail.tm"
    EMAIL_API_TIMEOUT: float = 30.0


settings = Settings()
