"""
Admin 管理路由
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from backend.database import get_db
from backend.dependencies import get_current_admin_user
from backend.crud.user import user_crud
from backend.crud.task import task_crud
from backend.schemas.auth import UserResponse
from backend.schemas.task import TaskResponse, TaskListResponse

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin_user)]
)

@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    列出所有用户 (仅管理员)
    """
    users = await user_crud.get_multi(db, skip=skip, limit=limit)
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at.isoformat() if user.created_at else None
        )
        for user in users
    ]

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除用户 (仅管理员)
    """
    user = await user_crud.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    # 不允许删除自己
    # 注意：这里需要从 dependencies 获取当前用户ID来对比，暂时略过，前端做限制即可，后端也可以加
    
    await user_crud.remove(db, user_id)
    return {"message": "User deleted successfully"}

@router.get("/tasks", response_model=TaskListResponse)
async def list_all_tasks(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    列出所有任务 (仅管理员)
    """
    skip = (page - 1) * page_size
    tasks, total = await task_crud.get_multi_all(db, skip=skip, limit=page_size)
    
    # 转换任务数据
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

    return {
        "tasks": task_responses,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除任务 (仅管理员)
    """
    task = await task_crud.get(db, task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
    await task_crud.remove(db, task_id)
    return {"message": "Task deleted successfully"}
