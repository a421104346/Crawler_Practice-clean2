"""
FastAPI 主应用程序
集成所有路由、中间件和启动事件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import os
import asyncio

# 在 Windows 上使用 ProactorEventLoop (解决 Playwright subprocess 问题)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 将根目录添加到 sys.path，以便能导入 core 和 crawlers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.database import init_db, close_db
from backend.routers import crawlers, tasks, websocket, auth, monitoring, admin
from backend.logger import setup_logging

# 配置日志系统
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库，关闭时清理资源
    """
    # 启动事件
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # 关闭事件
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shutdown complete")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="生产级爬虫管理系统 API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置中间件
from backend.middleware import RequestLoggingMiddleware, PerformanceMonitoringMiddleware

# 请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 性能监控中间件
app.add_middleware(PerformanceMonitoringMiddleware)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(crawlers.router)
app.include_router(tasks.router)
app.include_router(websocket.router)
app.include_router(monitoring.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """
    健康检查和欢迎页面
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
    健康检查端点（用于容器编排、负载均衡器等）
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    
    # 开发模式启动
    logger.info("Starting development server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level=settings.LOG_LEVEL.lower()
    )

