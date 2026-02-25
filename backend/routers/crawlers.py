"""
Crawler-related API routes
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
import os

from backend.database import get_db
from backend.schemas.crawler import CrawlerRequest, CrawlerResponse, CrawlerInfo
from backend.schemas.task import TaskCreate, TaskResponse
from backend.schemas.auth import TokenData
from backend.services.crawler_service import crawler_service
from backend.crud.task import task_crud
from backend.routers.websocket import manager
from backend.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/crawlers", tags=["crawlers"])

# Detect if Celery is enabled (via environment variable)
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
    Get all available crawlers list
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
    Get specific crawler details
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
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Launch crawler task (background execution)
    
    Args:
        crawler_type: Crawler type (yahoo, movies, jobs, etc.)
        request: Crawler request parameters
        background_tasks: FastAPI BackgroundTasks manager
        db: Database session
        current_user: Current logged-in user
    
    Returns:
        CrawlerResponse: Contains task ID and status
    """
    try:
        # 1. Validate crawler exists
        info = crawler_service.get_crawler_info(crawler_type)
        if not info:
            raise HTTPException(
                status_code=404,
                detail=f"Crawler '{crawler_type}' not found"
            )
        
        # 2. Prepare crawler parameters
        params = request.model_dump(exclude_unset=True, exclude={"extra_params"})
        if request.extra_params:
            params.update(request.extra_params)
        
        # 3. Create task record
        task_create = TaskCreate(
            crawler_type=crawler_type,
            params=params,
            user_id=current_user.user_id
        )
        task = await task_crud.create(db, task_create, user_id=current_user.user_id)
        
        logger.info(f"Created task {task.id} for crawler {crawler_type}")
        
        # 4. Submit task (Celery or BackgroundTasks)
        if USE_CELERY:
            # Use Celery async task queue
            celery_run_crawler.delay(task.id, crawler_type, params)
            logger.info(f"Task {task.id} submitted to Celery")
        else:
            # Use FastAPI BackgroundTasks (default)
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
    Execute crawler task in background
    
    This function runs in a background thread without blocking the API response
    """
    from backend.database import AsyncSessionLocal
    from backend.schemas.task import TaskUpdate
    from datetime import datetime
    
    try:
        logger.info(f"Executing task {task_id}: {crawler_type}")
        
        # 1. Update task status to running (using independent session)
        async with AsyncSessionLocal() as db:
            await task_crud.update(
                db,
                task_id,
                TaskUpdate(status="running", progress=0)
            )
        
        # 2. Broadcast task start
        await manager.broadcast_to_task(task_id, {
            "task_id": task_id,
            "status": "running",
            "progress": 0,
            "message": "Task started"
        })
        
        # 3. Define progress callback (each call uses independent session to prevent concurrency conflicts)
        async def progress_callback(progress: int, message: str):
            """Update progress to database and WebSocket"""
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
        
        # 4. Execute crawler
        result = await crawler_service.run_crawler(
            crawler_type,
            params,
            progress_callback=progress_callback
        )
        
        # 5. Update task status to completed (using independent session)
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
        
        # 6. Broadcast completion message
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
        
        # Update task status to failed (using independent session)
        async with AsyncSessionLocal() as db:
            await task_crud.update(
                db,
                task_id,
                TaskUpdate(
                    status="failed",
                    error=str(e)
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
