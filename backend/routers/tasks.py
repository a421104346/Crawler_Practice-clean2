"""
Task management API routes
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging
import json

from backend.database import get_db
from backend.schemas.task import TaskResponse, TaskListResponse, TaskUpdate
from backend.schemas.auth import TokenData
from backend.crud.task import task_crud
from backend.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get specific task details
    
    Args:
        task_id: Task ID
        db: Database session
        current_user: Current logged-in user
    
    Returns:
        TaskResponse: Task details
    """
    try:
        task = await task_crud.get(db, task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task '{task_id}' not found"
            )
        
        # Permission check: can only access own tasks (except admin)
        if task.user_id != current_user.user_id and current_user.username != "admin":
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this task"
            )
        
        # Convert JSON string fields back to objects
        task_dict = {
            "id": task.id,
            "crawler_type": task.crawler_type,
            "status": task.status,
            "progress": task.progress,
            "params": json.loads(task.params) if task.params else None,
            "result": json.loads(task.result) if task.result else None,
            "error": task.error,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "duration": task.duration,
            "user_id": task.user_id
        }
        
        return TaskResponse(**task_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task")


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Status filter"),
    crawler_type: Optional[str] = Query(None, description="Crawler type filter"),
    target_user_id: Optional[str] = Query(None, alias="user_id", description="User ID filter (admin only)"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get task list (supports pagination and filtering)
    
    Args:
        page: Page number (starting from 1)
        page_size: Items per page
        status: Status filter
        crawler_type: Crawler type filter
        target_user_id: Target user ID (admin only)
        db: Database session
        current_user: Current logged-in user
    
    Returns:
        TaskListResponse: Task list and total count
    """
    try:
        # Determine user ID to query
        # Default: can only view own tasks
        filter_user_id = current_user.user_id
        
        # Admin can view all tasks or specific user's tasks
        if current_user.username == "admin":
            if target_user_id:
                filter_user_id = target_user_id
            else:
                filter_user_id = None  # View all
        
        # Calculate offset
        skip = (page - 1) * page_size
        
        # Get task list
        tasks = await task_crud.get_multi(
            db,
            skip=skip,
            limit=page_size,
            status=status,
            crawler_type=crawler_type,
            user_id=filter_user_id
        )
        
        # Get total count
        total = await task_crud.count(
            db,
            status=status,
            crawler_type=crawler_type,
            user_id=filter_user_id
        )
        
        # Transform task data
        task_responses = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "crawler_type": task.crawler_type,
                "status": task.status,
                "progress": task.progress,
                "params": json.loads(task.params) if task.params else None,
                "result": json.loads(task.result) if task.result else None,
                "error": task.error,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "duration": task.duration,
                "user_id": task.user_id
            }
            task_responses.append(TaskResponse(**task_dict))
        
        return TaskListResponse(
            total=total,
            tasks=task_responses,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to list tasks")


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update task (e.g., cancel task)
    
    Args:
        task_id: Task ID
        task_update: Update content
        db: Database session
    
    Returns:
        TaskResponse: Updated task
    """
    try:
        task = await task_crud.update(db, task_id, task_update)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task '{task_id}' not found"
            )
        
        # Transform data
        task_dict = {
            "id": task.id,
            "crawler_type": task.crawler_type,
            "status": task.status,
            "progress": task.progress,
            "params": json.loads(task.params) if task.params else None,
            "result": json.loads(task.result) if task.result else None,
            "error": task.error,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "duration": task.duration,
            "user_id": task.user_id
        }
        
        return TaskResponse(**task_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update task")


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Delete task
    
    Args:
        task_id: Task ID
        db: Database session
        current_user: Current logged-in user
    
    Returns:
        Deletion confirmation message
    """
    try:
        # First get task to check permissions
        task = await task_crud.get(db, task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task '{task_id}' not found"
            )
            
        # Permission check
        if task.user_id != current_user.user_id and current_user.username != "admin":
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this task"
            )
            
        success = await task_crud.delete(db, task_id)
        if not success:
            # In theory task existence was already checked above; this is a safety net
             raise HTTPException(
                status_code=404,
                detail=f"Task '{task_id}' not found"
            )
        
        return {"message": f"Task {task_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete task")
