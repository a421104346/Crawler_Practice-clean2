"""
Configuration: manage environment variables and global settings
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Get current file directory (backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Project root directory
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Data directory configuration
DATA_DIR = os.path.join(BASE_DIR, "data")
# Auto-create data directory
os.makedirs(DATA_DIR, exist_ok=True)

# Database file path
DB_PATH = os.path.join(DATA_DIR, "crawler_tasks.db")

class Settings(BaseSettings):
    """Application configuration"""
    
    # Basic application settings
    APP_NAME: str = "Crawler Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database settings
    # SQLite (development) - use absolute path for consistency
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DB_PATH}"
    # PostgreSQL (production)
    POSTGRES_URL: Optional[str] = None  # Optional PostgreSQL URL
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    
    # JWT authentication settings (must be configured via environment variables)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Redis settings (Phase 2)
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Celery settings
    CELERY_BROKER_URL: Optional[str] = None  # Defaults to REDIS_URL
    CELERY_RESULT_BACKEND: Optional[str] = None  # Defaults to REDIS_URL
    USE_CELERY: bool = False
    
    # Log level
    LOG_LEVEL: str = "INFO"
    # Log directory (defaults to project root to avoid triggering hot reload)
    LOG_DIR: str = os.getenv("LOG_DIR", os.path.join(os.path.dirname(BASE_DIR), "logs"))

    # Firecrawl configuration
    FIRECRAWL_API_KEY: Optional[str] = os.getenv("FIRECRAWL_API_KEY")
    FIRECRAWL_BASE_URL: str = os.getenv("FIRECRAWL_BASE_URL", "https://api.firecrawl.dev")

    # Task recycle settings (seconds)
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


# Create global configuration instance
settings = Settings()
