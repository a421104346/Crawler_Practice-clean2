"""
数据库配置：SQLAlchemy + AsyncSession
支持 SQLite (开发) 和 PostgreSQL (生产)
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from fastapi import HTTPException
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# 选择数据库 URL（优先使用 PostgreSQL）
db_url = settings.POSTGRES_URL or settings.DATABASE_URL

# 根据数据库类型配置引擎参数
engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
    "pool_pre_ping": True,
}

# PostgreSQL 特殊配置
if "postgresql" in db_url:
    engine_kwargs.update({
        "pool_size": 10,  # 连接池大小
        "max_overflow": 20,  # 最大溢出连接数
        "pool_recycle": 3600,  # 1小时回收连接
        "pool_timeout": 30,  # 连接超时
    })
    logger.info("Using PostgreSQL database")
else:
    logger.info("Using SQLite database")

# 创建异步引擎
engine = create_async_engine(db_url, **engine_kwargs)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 创建基类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    依赖注入：获取数据库会话
    使用方法：
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except HTTPException:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库：创建所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
    logger.info("Database connection closed")
