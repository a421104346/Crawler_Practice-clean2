"""
爬虫相关的 Celery 任务
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
    Celery 任务：执行爬虫
    
    Args:
        self: Celery task 实例
        task_id: 任务 ID
        crawler_type: 爬虫类型
        params: 爬虫参数
    
    Returns:
        任务结果
    """
    logger.info(f"Celery task started: {task_id} - {crawler_type}")
    
    # 在新的事件循环中运行异步代码
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
    异步执行爬虫（内部函数）
    
    Args:
        task_id: 任务 ID
        crawler_type: 爬虫类型
        params: 爬虫参数
        celery_task: Celery 任务实例
    """
    async with AsyncSessionLocal() as db:
        try:
            # 1. 更新任务状态为 running
            await task_crud.update(
                db,
                task_id,
                TaskUpdate(
                    status="running",
                    progress=0,
                    started_at=datetime.utcnow()
                )
            )
            
            # 2. 广播任务开始
            await manager.broadcast_to_task(task_id, {
                "task_id": task_id,
                "status": "running",
                "progress": 0,
                "message": "Task started in Celery worker"
            })
            
            # 3. 定义进度回调
            async def progress_callback(progress: int, message: str):
                """更新进度到数据库和 WebSocket"""
                # 更新 Celery 任务状态
                celery_task.update_state(
                    state="PROGRESS",
                    meta={"progress": progress, "message": message}
                )
                
                # 更新数据库
                await task_crud.update(
                    db,
                    task_id,
                    TaskUpdate(progress=progress)
                )
                
                # 广播到 WebSocket
                await manager.broadcast_to_task(task_id, {
                    "task_id": task_id,
                    "status": "running",
                    "progress": progress,
                    "message": message
                })
            
            # 4. 执行爬虫
            logger.info(f"Executing crawler: {crawler_type}")
            result = await crawler_service.run_crawler(
                crawler_type,
                params,
                progress_callback=progress_callback
            )
            
            # 5. 更新任务状态为 completed
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
            
            # 6. 广播完成消息
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
            
            # 更新任务状态为 failed
            await task_crud.update(
                db,
                task_id,
                TaskUpdate(
                    status="failed",
                    error=str(e),
                    completed_at=datetime.utcnow()
                )
            )
            
            # 广播失败消息
            await manager.broadcast_to_task(task_id, {
                "task_id": task_id,
                "status": "failed",
                "progress": 0,
                "message": f"Task failed: {str(e)}",
                "error": str(e)
            })
            
            # 重新抛出异常让 Celery 处理
            raise


@celery_app.task(name="crawler_tasks.cleanup_old_tasks")
def cleanup_old_tasks(days: int = 30):
    """
    清理旧任务（定期任务）
    
    Args:
        days: 保留多少天内的任务
    
    Returns:
        清理的任务数量
    """
    logger.info(f"Starting cleanup of tasks older than {days} days")
    
    # TODO: 实现清理逻辑
    # 1. 删除超过 N 天的 completed 任务
    # 2. 删除超过 N 天的 failed 任务
    # 3. 保留 running 和 pending 任务
    
    return {"cleaned": 0}


@celery_app.task(name="crawler_tasks.health_check")
def health_check():
    """
    健康检查任务
    
    Returns:
        健康状态
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "worker": "celery"
    }
