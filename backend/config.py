"""
配置文件：管理环境变量和全局设置
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# 获取当前文件所在目录 (backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录
PROJECT_ROOT = os.path.dirname(BASE_DIR)

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
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    
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
    USE_CELERY: bool = False
    
    # 日志级别
    LOG_LEVEL: str = "INFO"
    # 日志目录（默认放在项目根目录，避免触发热重载）
    LOG_DIR: str = os.getenv("LOG_DIR", os.path.join(os.path.dirname(BASE_DIR), "logs"))

    # Firecrawl 配置
    FIRECRAWL_API_KEY: Optional[str] = os.getenv("FIRECRAWL_API_KEY")
    FIRECRAWL_BASE_URL: str = os.getenv("FIRECRAWL_BASE_URL", "https://api.firecrawl.dev")

    # 任务回收设置（秒）
    TASK_RECYCLE_INTERVAL_SECONDS: int = int(os.getenv("TASK_RECYCLE_INTERVAL_SECONDS", "300"))
    TASK_RUNNING_TIMEOUT_SECONDS: int = int(os.getenv("TASK_RUNNING_TIMEOUT_SECONDS", "1800"))

    # Admin bootstrap (create_admin.py)
    ADMIN_USERNAME: Optional[str] = None
    ADMIN_EMAIL: Optional[str] = None
    ADMIN_PASSWORD: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=(os.path.join(PROJECT_ROOT, ".env"), os.path.join(BASE_DIR, ".env")),
        case_sensitive=True
    )


# 创建全局配置实例
settings = Settings()
