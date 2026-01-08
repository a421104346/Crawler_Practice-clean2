"""
任务 CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from backend.models.task import TaskModel
from backend.schemas.task import TaskCreate, TaskUpdate
from typing import Optional, List
from datetime import datetime
import json


class TaskCRUD:
    """任务的 CRUD 操作"""
    
    async def create(
        self, 
        db: AsyncSession, 
        task_in: TaskCreate
    ) -> TaskModel:
        """创建新任务"""
        # 将 params dict 转换为 JSON 字符串
        params_json = json.dumps(task_in.params) if task_in.params else None
        
        task = TaskModel(
            crawler_type=task_in.crawler_type,
            params=params_json,
            user_id=task_in.user_id,
            status="pending",
            progress=0
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    async def get(
        self, 
        db: AsyncSession, 
        task_id: str
    ) -> Optional[TaskModel]:
        """根据ID获取任务"""
        result = await db.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        crawler_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[TaskModel]:
        """获取任务列表（带过滤和分页）"""
        query = select(TaskModel)
        
        # 添加过滤条件
        if status:
            query = query.where(TaskModel.status == status)
        if crawler_type:
            query = query.where(TaskModel.crawler_type == crawler_type)
        if user_id:
            query = query.where(TaskModel.user_id == user_id)
        
        # 按创建时间倒序
        query = query.order_by(TaskModel.created_at.desc())
        
        # 分页
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        crawler_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> int:
        """统计任务数量"""
        query = select(func.count()).select_from(TaskModel)
        
        if status:
            query = query.where(TaskModel.status == status)
        if crawler_type:
            query = query.where(TaskModel.crawler_type == crawler_type)
        if user_id:
            query = query.where(TaskModel.user_id == user_id)
        
        result = await db.execute(query)
        return result.scalar()
    
    async def update(
        self,
        db: AsyncSession,
        task_id: str,
        task_update: TaskUpdate
    ) -> Optional[TaskModel]:
        """更新任务"""
        # 获取任务
        task = await self.get(db, task_id)
        if not task:
            return None
        
        # 更新字段
        update_data = task_update.model_dump(exclude_unset=True)
        
        # 特殊处理：将result转换为JSON字符串
        if "result" in update_data and update_data["result"] is not None:
            update_data["result"] = json.dumps(update_data["result"])
        
        # 如果状态变为 running，记录开始时间
        if update_data.get("status") == "running" and not task.started_at:
            update_data["started_at"] = datetime.utcnow()
        
        # 如果状态变为 completed 或 failed，记录完成时间和计算时长
        if update_data.get("status") in ["completed", "failed"]:
            if not task.completed_at:
                update_data["completed_at"] = datetime.utcnow()
                if task.started_at:
                    duration = (datetime.utcnow() - task.started_at).total_seconds()
                    update_data["duration"] = duration
        
        # 执行更新
        for key, value in update_data.items():
            setattr(task, key, value)
        
        await db.commit()
        await db.refresh(task)
        return task
    
    async def delete(
        self,
        db: AsyncSession,
        task_id: str
    ) -> bool:
        """删除任务"""
        result = await db.execute(
            delete(TaskModel).where(TaskModel.id == task_id)
        )
        await db.commit()
        return result.rowcount > 0


# 创建全局实例
task_crud = TaskCRUD()
