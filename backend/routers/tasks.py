"""
任务管理的API路由
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
    获取特定任务的详细信息
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        TaskResponse: 任务详情
    """
    try:
        task = await task_crud.get(db, task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task '{task_id}' not found"
            )
        
        # 权限检查：只能访问自己的任务（管理员除外）
        if task.user_id != current_user.user_id and current_user.username != "admin":
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this task"
            )
        
        # 将 JSON 字符串字段转换回对象
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
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="任务状态过滤"),
    crawler_type: Optional[str] = Query(None, description="爬虫类型过滤"),
    target_user_id: Optional[str] = Query(None, alias="user_id", description="用户ID过滤（仅管理员可用）"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    获取任务列表（支持分页和过滤）
    
    Args:
        page: 页码（从1开始）
        page_size: 每页数量
        status: 状态过滤
        crawler_type: 爬虫类型过滤
        target_user_id: 目标用户ID（仅管理员可用）
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        TaskListResponse: 任务列表和总数
    """
    try:
        # 确定要查询的用户ID
        # 默认只能查看自己的任务
        filter_user_id = current_user.user_id
        
        # 管理员可以查看所有任务，或指定用户的任务
        if current_user.username == "admin":
            if target_user_id:
                filter_user_id = target_user_id
            else:
                filter_user_id = None  # 查看所有
        
        # 计算偏移量
        skip = (page - 1) * page_size
        
        # 获取任务列表
        tasks = await task_crud.get_multi(
            db,
            skip=skip,
            limit=page_size,
            status=status,
            crawler_type=crawler_type,
            user_id=filter_user_id
        )
        
        # 获取总数
        total = await task_crud.count(
            db,
            status=status,
            crawler_type=crawler_type,
            user_id=filter_user_id
        )
        
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
    更新任务（例如取消任务）
    
    Args:
        task_id: 任务ID
        task_update: 更新内容
        db: 数据库会话
    
    Returns:
        TaskResponse: 更新后的任务
    """
    try:
        task = await task_crud.update(db, task_id, task_update)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task '{task_id}' not found"
            )
        
        # 转换数据
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
    删除任务
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        删除确认消息
    """
    try:
        # 先获取任务检查权限
        task = await task_crud.get(db, task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task '{task_id}' not found"
            )
            
        # 权限检查
        if task.user_id != current_user.user_id and current_user.username != "admin":
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this task"
            )
            
        success = await task_crud.delete(db, task_id)
        if not success:
            # 理论上上面已经检查过 task 存在，这里是个双重保险
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
