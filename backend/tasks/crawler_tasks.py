"""
Crawler-related Celery tasks
"""
from backend.celery_app import celery_app
from backend.database import AsyncSessionLocal
from backend.crud.task import task_crud
from backend.schemas.task import TaskUpdate
from backend.services.crawler_service import crawler_service
from backend.routers.websocket import manager
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="crawler_tasks.run_crawler")
def run_crawler_task(self, task_id: str, crawler_type: str, params: dict):
    """
    Celery task: execute crawler
    
    Args:
        self: Celery task instance
        task_id: Task ID
        crawler_type: Crawler type
        params: Crawler parameters
    
    Returns:
        Task result
    """
    logger.info(f"Celery task started: {task_id} - {crawler_type}")
    
    # Run async code in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            _execute_crawler_async(task_id, crawler_type, params, self)
        )
        return result
    finally:
        loop.close()


async def _execute_crawler_async(
    task_id: str, 
    crawler_type: str, 
    params: dict,
    celery_task
):
    """
    Execute crawler asynchronously (internal function)
    
    Args:
        task_id: Task ID
        crawler_type: Crawler type
        params: Crawler parameters
        celery_task: Celery task instance
    """
    async with AsyncSessionLocal() as db:
        try:
            # 1. Update task status to running
            await task_crud.update(
                db,
                task_id,
                TaskUpdate(
                    status="running",
                    progress=0,
                    started_at=datetime.utcnow()
                )
            )
            
            # 2. Broadcast task started
            await manager.broadcast_to_task(task_id, {
                "task_id": task_id,
                "status": "running",
                "progress": 0,
                "message": "Task started in Celery worker"
            })
            
            # 3. Define progress callback
            async def progress_callback(progress: int, message: str):
                """Update progress to database and WebSocket"""
                # Update Celery task status
                celery_task.update_state(
                    state="PROGRESS",
                    meta={"progress": progress, "message": message}
                )
                
                # Update database
                await task_crud.update(
                    db,
                    task_id,
                    TaskUpdate(progress=progress)
                )
                
                # Broadcast to WebSocket
                await manager.broadcast_to_task(task_id, {
                    "task_id": task_id,
                    "status": "running",
                    "progress": progress,
                    "message": message
                })
            
            # 4. Execute crawler
            logger.info(f"Executing crawler: {crawler_type}")
            result = await crawler_service.run_crawler(
                crawler_type,
                params,
                progress_callback=progress_callback
            )
            
            # 5. Update task status to completed
            await task_crud.update(
                db,
                task_id,
                TaskUpdate(
                    status="completed",
                    progress=100,
                    result=result,
                    completed_at=datetime.utcnow()
                )
            )
            
            # 6. Broadcast completion message
            await manager.broadcast_to_task(task_id, {
                "task_id": task_id,
                "status": "completed",
                "progress": 100,
                "message": "Task completed successfully",
                "result": result
            })
            
            logger.info(f"Task {task_id} completed successfully")
            return {"status": "success", "result": result}
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}", exc_info=True)
            
            # Update task status to failed
            await task_crud.update(
                db,
                task_id,
                TaskUpdate(
                    status="failed",
                    error=str(e),
                    completed_at=datetime.utcnow()
                )
            )
            
            # Broadcast failure message
            await manager.broadcast_to_task(task_id, {
                "task_id": task_id,
                "status": "failed",
                "progress": 0,
                "message": f"Task failed: {str(e)}",
                "error": str(e)
            })
            
            # Re-raise exception for Celery to handle
            raise


@celery_app.task(name="crawler_tasks.cleanup_old_tasks")
def cleanup_old_tasks(days: int = 30):
    """
    Clean up old tasks (periodic task)
    
    Args:
        days: Number of days to retain tasks
    
    Returns:
        Number of cleaned tasks
    """
    logger.info(f"Starting cleanup of tasks older than {days} days")
    
    # TODO: Implement cleanup logic
    # 1. Delete completed tasks older than N days
    # 2. Delete failed tasks older than N days
    # 3. Keep running and pending tasks
    
    return {"cleaned": 0}


@celery_app.task(name="crawler_tasks.health_check")
def health_check():
    """
    Health check task
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "worker": "celery"
    }
