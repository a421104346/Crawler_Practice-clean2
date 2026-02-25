"""
Performance monitoring and metrics collection
"""
import psutil
import time
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Performance monitor"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system metrics
        
        Returns:
            System metrics dictionary
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                },
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def get_app_metrics(self) -> Dict[str, Any]:
        """
        Get application metrics
        
        Returns:
            Application metrics dictionary
        """
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """
        Format uptime
        
        Args:
            seconds: Number of seconds
        
        Returns:
            Formatted time string
        """
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"{days}d {hours}h {minutes}m {secs}s"
    
    def increment_request(self):
        """Increment request count"""
        self.request_count += 1
    
    def increment_error(self):
        """Increment error count"""
        self.error_count += 1


# Global monitor instance
monitor = PerformanceMonitor()


async def check_database_health() -> Dict[str, Any]:
    """
    Check database health status
    
    Returns:
        Health status dictionary
    """
    from backend.database import AsyncSessionLocal
    from sqlalchemy import text
    
    try:
        async with AsyncSessionLocal() as session:
            # Execute simple query
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            
            return {
                "status": "healthy",
                "message": "Database connection successful"
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}"
        }


async def check_redis_health() -> Dict[str, Any]:
    """
    Check Redis health status
    
    Returns:
        Health status dictionary
    """
    try:
        import redis
        from backend.config import settings
        
        if not settings.REDIS_URL:
            return {"status": "not_configured"}
        
        # Connect to Redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        
        return {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Redis error: {str(e)}"
        }


async def check_celery_health() -> Dict[str, Any]:
    """
    Check Celery health status
    
    Returns:
        Health status dictionary
    """
    try:
        from backend.celery_app import celery_app
        
        # Check if Celery is available
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            worker_count = len(stats)
            return {
                "status": "healthy",
                "message": f"Celery workers: {worker_count}",
                "workers": list(stats.keys())
            }
        else:
            return {
                "status": "unhealthy",
                "message": "No Celery workers available"
            }
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        return {
            "status": "unknown",
            "message": f"Celery check error: {str(e)}"
        }
