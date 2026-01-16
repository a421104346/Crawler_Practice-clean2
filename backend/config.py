"""
配置文件：管理环境变量和全局设置
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

# 获取当前文件所在目录 (backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据目录配置
DATA_DIR = os.path.join(BASE_DIR, "data")
# 自动创建数据目录
os.makedirs(DATA_DIR, exist_ok=True)

# 数据库文件路径
DB_PATH = os.path.join(DATA_DIR, "crawler_tasks.db")

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础设置
    APP_NAME: str = "Crawler Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库设置
    # SQLite (开发环境) - 使用绝对路径确保一致性
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DB_PATH}"
    # PostgreSQL (生产环境)
    POSTGRES_URL: Optional[str] = None  # 可选的 PostgreSQL URL
    
    # JWT 认证设置（务必通过环境变量配置）
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS 设置
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Redis 设置 (Phase 2)
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Celery 设置
    CELERY_BROKER_URL: Optional[str] = None  # 默认使用 REDIS_URL
    CELERY_RESULT_BACKEND: Optional[str] = None  # 默认使用 REDIS_URL
    
    # 日志级别
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
