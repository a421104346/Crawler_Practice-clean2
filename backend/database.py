"""
Database configuration: SQLAlchemy + AsyncSession
Supports SQLite (development) and PostgreSQL (production)
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from fastapi import HTTPException
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# Select database URL (prefer PostgreSQL)
db_url = settings.POSTGRES_URL or settings.DATABASE_URL

# Configure engine parameters based on database type
engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
    "pool_pre_ping": True,
}

# PostgreSQL-specific configuration
if "postgresql" in db_url:
    engine_kwargs.update({
        "pool_size": 10,  # Connection pool size
        "max_overflow": 20,  # Max overflow connections
        "pool_recycle": 3600,  # Recycle connections every hour
        "pool_timeout": 30,  # Connection timeout
    })
    logger.info("Using PostgreSQL database")
else:
    logger.info("Using SQLite database")

# Create async engine
engine = create_async_engine(db_url, **engine_kwargs)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create base class
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency injection: get database session
    Usage:
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
    """Initialize database: create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def close_db():
    """Close database connection"""
    await engine.dispose()
    logger.info("Database connection closed")
