"""
监控和健康检查 API 路由
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging
from datetime import datetime

from backend.monitoring import (
    monitor,
    check_database_health,
    check_redis_health,
    check_celery_health
)
from backend.dependencies import get_current_admin_user
from backend.schemas.auth import TokenData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/health")
async def health_check():
    """
    基础健康检查（无需认证）
    
    Returns:
        健康状态
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "crawler-api"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """
    详细健康检查
    检查所有依赖服务的状态
    
    Returns:
        详细健康状态
    """
    # 并发检查所有服务
    db_health = await check_database_health()
    redis_health = await check_redis_health()
    celery_health = await check_celery_health()
    
    # 判断整体健康状态
    all_healthy = all([
        db_health.get("status") == "healthy",
        redis_health.get("status") in ["healthy", "not_configured"],
        celery_health.get("status") in ["healthy", "unknown"],
    ])
    
    overall_status = "healthy" if all_healthy else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": {
            "database": db_health,
            "redis": redis_health,
            "celery": celery_health,
        }
    }


@router.get("/metrics", dependencies=[Depends(get_current_admin_user)])
async def get_metrics(
    current_user: TokenData = Depends(get_current_admin_user)
):
    """
    获取系统指标（需要管理员权限）
    
    Args:
        current_user: 当前用户（管理员）
    
    Returns:
        系统和应用指标
    """
    system_metrics = monitor.get_system_metrics()
    app_metrics = monitor.get_app_metrics()
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "system": system_metrics,
        "application": app_metrics,
    }


@router.get("/stats")
async def get_stats():
    """
    获取简单统计信息（无需认证）
    
    Returns:
        统计信息
    """
    from backend.database import AsyncSessionLocal
    from backend.crud.task import task_crud
    
    async with AsyncSessionLocal() as db:
        # 获取任务统计
        total_tasks = await task_crud.count(db)
        completed_tasks = await task_crud.count(db, status="completed")
        failed_tasks = await task_crud.count(db, status="failed")
        running_tasks = await task_crud.count(db, status="running")
        
        return {
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "running": running_tasks,
                "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            },
            "uptime": monitor.get_app_metrics()["uptime_formatted"],
        }
