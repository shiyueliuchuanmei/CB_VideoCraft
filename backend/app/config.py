"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用信息
    APP_NAME: str = "VideoCraft"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./videocraft.db"
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174"
    
    # 文件存储配置
    STORAGE_TYPE: str = "local"  # local 或 oss
    LOCAL_STORAGE_PATH: str = "./uploads"
    
    # 阿里云 OSS 配置（可选）
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_BUCKET: str = ""
    OSS_ENDPOINT: str = ""
    
    # 豆包 API 配置
    DOUBAO_API_KEY: str = ""
    SEEDREAM_ENDPOINT: str = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    SEEDANCE_ENDPOINT: str = "https://ark.cn-beijing.volces.com/api/v3/videos/generations"
    
    # JWT 配置
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
