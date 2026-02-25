"""
Monitoring and health check API routes
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
    Basic health check (no authentication required)
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "crawler-api"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check
    Checks status of all dependent services
    
    Returns:
        Detailed health status
    """
    # Concurrently check all services
    db_health = await check_database_health()
    redis_health = await check_redis_health()
    celery_health = await check_celery_health()
    
    # Determine overall health status
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
    Get system metrics (requires admin privileges)
    
    Args:
        current_user: Current user (admin)
    
    Returns:
        System and application metrics
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
    Get simple statistics (no authentication required)
    
    Returns:
        Statistics
    """
    from backend.database import AsyncSessionLocal
    from backend.crud.task import task_crud
    
    async with AsyncSessionLocal() as db:
        # Get task statistics
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
