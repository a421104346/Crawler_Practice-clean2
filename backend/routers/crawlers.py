"""
爬虫相关的API路由
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
import os

from backend.database import get_db
from backend.schemas.crawler import CrawlerRequest, CrawlerResponse, CrawlerInfo
from backend.schemas.task import TaskCreate, TaskResponse
from backend.services.crawler_service import crawler_service
from backend.crud.task import task_crud
from backend.routers.websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/crawlers", tags=["crawlers"])

# 检测是否启用 Celery（通过环境变量）
USE_CELERY = os.getenv("USE_CELERY", "false").lower() == "true"

if USE_CELERY:
    try:
        from backend.tasks.crawler_tasks import run_crawler_task as celery_run_crawler
        logger.info("Celery integration enabled")
    except ImportError:
        logger.warning("Celery not available, falling back to BackgroundTasks")
        USE_CELERY = False


@router.get("", response_model=List[CrawlerInfo])
async def list_crawlers():
    """
    获取所有可用的爬虫列表
    """
    try:
        crawlers = crawler_service.list_crawlers()
        return crawlers
    except Exception as e:
        logger.error(f"Error listing crawlers: {e}")
        raise HTTPException(status_code=500, detail="Failed to list crawlers")


@router.get("/{crawler_type}", response_model=CrawlerInfo)
async def get_crawler_info(crawler_type: str):
    """
    获取特定爬虫的详细信息
    """
    info = crawler_service.get_crawler_info(crawler_type)
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Crawler '{crawler_type}' not found"
        )
    return info


@router.post("/{crawler_type}/run", response_model=CrawlerResponse)
async def run_crawler(
    crawler_type: str,
    request: CrawlerRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    启动爬虫任务（后台运行）
    
    Args:
        crawler_type: 爬虫类型 (yahoo, movies, jobs等)
        request: 爬虫请求参数
        background_tasks: FastAPI 后台任务管理器
        db: 数据库会话
    
    Returns:
        CrawlerResponse: 包含任务ID和状态
    """
    try:
        # 1. 验证爬虫是否存在
        info = crawler_service.get_crawler_info(crawler_type)
        if not info:
            raise HTTPException(
                status_code=404,
                detail=f"Crawler '{crawler_type}' not found"
            )
        
        # 2. 准备爬虫参数
        params = request.model_dump(exclude_unset=True, exclude={"extra_params"})
        if request.extra_params:
            params.update(request.extra_params)
        
        # 3. 创建任务记录
        task_create = TaskCreate(
            crawler_type=crawler_type,
            params=params
        )
        task = await task_crud.create(db, task_create)
        
        logger.info(f"Created task {task.id} for crawler {crawler_type}")
        
        # 4. 提交任务（Celery 或 BackgroundTasks）
        if USE_CELERY:
            # 使用 Celery 异步任务队列
            celery_run_crawler.delay(task.id, crawler_type, params)
            logger.info(f"Task {task.id} submitted to Celery")
        else:
            # 使用 FastAPI BackgroundTasks（默认）
            background_tasks.add_task(
                execute_crawler_task,
                task_id=task.id,
                crawler_type=crawler_type,
                params=params
            )
            logger.info(f"Task {task.id} submitted to BackgroundTasks")
        
        return CrawlerResponse(
            status="success",
            task_id=task.id,
            message=f"Task created successfully. Crawler '{crawler_type}' is starting...",
            timestamp=task.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting crawler {crawler_type}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start crawler: {str(e)}"
        )


async def execute_crawler_task(
    task_id: str,
    crawler_type: str,
    params: dict
):
    """
    后台执行爬虫任务
    
    这个函数在后台线程中运行，不会阻塞API响应
    """
    from backend.database import AsyncSessionLocal
    from backend.schemas.task import TaskUpdate
    from datetime import datetime
    
    try:
        logger.info(f"Executing task {task_id}: {crawler_type}")
        
        # 1. 更新任务状态为 running (使用独立的会话)
        async with AsyncSessionLocal() as db:
            await task_crud.update(
                db,
                task_id,
                TaskUpdate(status="running", progress=0)
            )
        
        # 2. 广播任务开始
        await manager.broadcast_to_task(task_id, {
            "task_id": task_id,
            "status": "running",
            "progress": 0,
            "message": "Task started"
        })
        
        # 3. 定义进度回调函数 (每次调用使用独立的会话，防止并发冲突)
        async def progress_callback(progress: int, message: str):
            """更新进度到数据库和WebSocket"""
            logger.info(f"Progress callback triggered: {progress}% - {message}")
            try:
                async with AsyncSessionLocal() as db:
                    await task_crud.update(
                        db,
                        task_id,
                        TaskUpdate(progress=progress)
                    )
                await manager.broadcast_to_task(task_id, {
                    "task_id": task_id,
                    "status": "running",
                    "progress": progress,
                    "message": message
                })
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
        
        # 4. 执行爬虫
        result = await crawler_service.run_crawler(
            crawler_type,
            params,
            progress_callback=progress_callback
        )
        
        # 5. 更新任务状态为 completed (使用独立的会话)
        async with AsyncSessionLocal() as db:
            await task_crud.update(
                db,
                task_id,
                TaskUpdate(
                    status="completed",
                    progress=100,
                    result=result
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
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}", exc_info=True)
        
        # 更新任务状态为 failed (使用独立的会话)
        async with AsyncSessionLocal() as db:
            await task_crud.update(
                db,
                task_id,
                TaskUpdate(
                    status="failed",
                    error=str(e)
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
