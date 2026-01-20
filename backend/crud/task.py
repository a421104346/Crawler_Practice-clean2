"""
任务 CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from backend.models.task import TaskModel
from backend.schemas.task import TaskCreate, TaskUpdate
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import json


class TaskCRUD:
    """任务的 CRUD 操作"""
    
    async def get_multi_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[TaskModel], int]:
        """获取所有任务（管理员用，返回列表和总数）"""
        # 查询总数
        count_query = select(func.count()).select_from(TaskModel)
        total = await db.scalar(count_query)
        
        # 查询数据
        query = select(TaskModel).order_by(TaskModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all(), total

    async def remove(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[TaskModel]:
        """删除任务并返回被删除的对象"""
        task = await self.get(db, task_id)
        if task:
            await db.delete(task)
            await db.commit()
        return task

    async def create(
        self, 
        db: AsyncSession, 
        task_in: TaskCreate,
        user_id: str
    ) -> TaskModel:
        """创建新任务"""
        # 将 params dict 转换为 JSON 字符串
        params_json = json.dumps(task_in.params) if task_in.params else None
        
        task = TaskModel(
            crawler_type=task_in.crawler_type,
            params=params_json,
            user_id=user_id,
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
        task_id: str,
        user_id: Optional[str] = None
    ) -> Optional[TaskModel]:
        """根据ID获取任务（可选验证用户）"""
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        if user_id:
            stmt = stmt.where(TaskModel.user_id == user_id)
            
        result = await db.execute(stmt)
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
        task_update: TaskUpdate,
        user_id: Optional[str] = None
    ) -> Optional[TaskModel]:
        """更新任务"""
        # 获取任务
        task = await self.get(db, task_id, user_id)
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
                started_at = task.started_at
                if started_at and started_at.tzinfo is not None:
                    now = datetime.now(timezone.utc)
                else:
                    now = datetime.utcnow()

                update_data["completed_at"] = now
                if started_at:
                    duration = (now - started_at).total_seconds()
                    update_data["duration"] = duration
        
        # 执行更新
        for key, value in update_data.items():
            setattr(task, key, value)
        
        await db.commit()
        await db.refresh(task)
        return task

    async def recycle_stale_running(
        self,
        db: AsyncSession,
        timeout_seconds: int
    ) -> int:
        """回收运行超时的任务，返回更新数量"""
        if timeout_seconds <= 0:
            return 0

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=timeout_seconds)

        stale_started = and_(TaskModel.started_at.isnot(None), TaskModel.started_at < cutoff)
        stale_unstarted = and_(TaskModel.started_at.is_(None), TaskModel.created_at < cutoff)

        stmt = (
            update(TaskModel)
            .where(TaskModel.status == "running")
            .where(or_(stale_started, stale_unstarted))
            .values(
                status="failed",
                error="Task timed out",
                completed_at=now
            )
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount or 0
    
    async def delete(
        self,
        db: AsyncSession,
        task_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """删除任务"""
        stmt = delete(TaskModel).where(TaskModel.id == task_id)
        if user_id:
            stmt = stmt.where(TaskModel.user_id == user_id)
            
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0


# 创建全局实例
task_crud = TaskCRUD()
