"""
FastAPI main application
Integrates all routers, middleware, and startup events
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import os
import asyncio

# Use ProactorEventLoop on Windows (fixes Playwright subprocess issues)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Add root directory to sys.path for importing core and crawlers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.database import init_db, close_db
from backend.routers import crawlers, tasks, websocket, auth, monitoring, admin, firecrawl
from backend.logger import setup_logging

# Configure logging system
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management
    Initialize database on startup, clean up resources on shutdown
    """
    # Startup event
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")

    recycler_task = None
    if settings.TASK_RECYCLE_INTERVAL_SECONDS > 0 and settings.TASK_RUNNING_TIMEOUT_SECONDS > 0:
        async def recycle_loop():
            from backend.database import AsyncSessionLocal
            from backend.crud.task import task_crud
            while True:
                try:
                    async with AsyncSessionLocal() as db:
                        recycled = await task_crud.recycle_stale_running(
                            db,
                            timeout_seconds=settings.TASK_RUNNING_TIMEOUT_SECONDS
                        )
                    if recycled:
                        logger.warning(f"Recycled {recycled} stale running tasks")
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    logger.error(f"Task recycle loop error: {exc}", exc_info=True)
                await asyncio.sleep(settings.TASK_RECYCLE_INTERVAL_SECONDS)

        recycler_task = asyncio.create_task(recycle_loop())
    
    yield
    
    # Shutdown event
    logger.info("Shutting down application...")
    if recycler_task:
        recycler_task.cancel()
        try:
            await recycler_task
        except asyncio.CancelledError:
            pass
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade crawler management system API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure middleware
from backend.middleware import RequestLoggingMiddleware, PerformanceMonitoringMiddleware

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Performance monitoring middleware
app.add_middleware(PerformanceMonitoringMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(crawlers.router)
app.include_router(tasks.router)
app.include_router(websocket.router)
app.include_router(monitoring.router)
app.include_router(admin.router)
app.include_router(firecrawl.router)


@app.get("/")
async def root():
    """
    Health check and welcome page
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api_prefix": "/api"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint (for container orchestration, load balancers, etc.)
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    
    # Development mode startup
    logger.info("Starting development server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload in development mode
        # Exclude log files to avoid hot reload loops triggered by log writes
        reload_excludes=["logs/*", "logs/*.log", "data/*.db", "__pycache__/*"],
        log_level=settings.LOG_LEVEL.lower()
    )

