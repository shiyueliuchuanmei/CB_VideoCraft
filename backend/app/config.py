"""
应用配置
"""
import os
import warnings
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

# 项目根目录（backend/ 的上级）
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """应用配置类"""

    # 应用信息
    APP_NAME: str = "CC_VideoCraft"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = ""
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # 数据库配置 - 使用绝对路径，避免 CWD 不同导致数据库文件位置不一致
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'cb_videocraft.db'}"
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:5174"
    
    # 文件存储配置
    STORAGE_TYPE: str = "local"  # local 或 oss
    LOCAL_STORAGE_PATH: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB
    UPLOAD_DIR: str = "uploads"
    
    # 阿里云 OSS 配置（可选）
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_BUCKET: str = ""
    OSS_ENDPOINT: str = ""
    
    # 飞书（ Lark）OAuth 配置
    FEISHU_APP_ID: str = ""
    FEISHU_APP_SECRET: str = ""
    FEISHU_REDIRECT_URI: str = "http://localhost:5174/api/auth/feishu/callback"

    # 豆包 API 配置
    DOUBAO_API_KEY: str = ""
    DOUBAO_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    SEEDREAM_ENDPOINT: str = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    SEEDANCE_ENDPOINT: str = "https://ark.cn-beijing.volces.com/api/v3/videos/generations"

    # 火山方舟模型接入点 ID（在方舟控制台创建接入点后填入）
    SEEDREAM_MODEL_ID: str = ""  # Seedream 图片生成模型接入点 ID，如 ep-20250101xxxxx
    SEEDANCE_MODEL_ID: str = ""  # Seedance 视频生成模型接入点 ID，如 ep-20250101xxxxx
    
    # JWT 配置
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def _validate_settings(s: Settings):
    """验证关键配置"""
    # 生产环境验证
    if s.APP_ENV == "production":
        if not s.SECRET_KEY or len(s.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY 必须设置且长度至少 32 字符！"
                "生成方法：python -c \"import secrets; print(secrets.token_hex(32))\""
            )
    # 开发环境警告
    elif s.DEBUG and not s.SECRET_KEY:
        warnings.warn(
            "警告：未设置 SECRET_KEY，生产环境请设置强密钥。",
            UserWarning
        )


# 全局配置实例
settings = Settings()

# 验证配置
_validate_settings(settings)
