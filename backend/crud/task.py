"""
Task CRUD operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from backend.models.task import TaskModel
from backend.schemas.task import TaskCreate, TaskUpdate
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import json


class TaskCRUD:
    """Task CRUD operations"""
    
    async def get_multi_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[TaskModel], int]:
        """Get all tasks (admin, returns list and count)"""
        # Query total count
        count_query = select(func.count()).select_from(TaskModel)
        total = await db.scalar(count_query)
        
        # Query data
        query = select(TaskModel).order_by(TaskModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all(), total

    async def remove(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[TaskModel]:
        """Delete task and return the deleted object"""
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
        """Create new task"""
        # Convert params dict to JSON string
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
        """Get task by ID (optionally verify user)"""
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
        """Get task list (with filtering and pagination)"""
        query = select(TaskModel)
        
        # Add filter conditions
        if status:
            query = query.where(TaskModel.status == status)
        if crawler_type:
            query = query.where(TaskModel.crawler_type == crawler_type)
        if user_id:
            query = query.where(TaskModel.user_id == user_id)
        
        # Order by creation time descending
        query = query.order_by(TaskModel.created_at.desc())
        
        # Pagination
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
        """Count tasks"""
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
        """Update task"""
        # Get task
        task = await self.get(db, task_id, user_id)
        if not task:
            return None
        
        # Update fields
        update_data = task_update.model_dump(exclude_unset=True)
        
        # Special handling: convert result to JSON string
        if "result" in update_data and update_data["result"] is not None:
            update_data["result"] = json.dumps(update_data["result"])
        
        # If status changes to running, record start time
        if update_data.get("status") == "running" and not task.started_at:
            update_data["started_at"] = datetime.utcnow()
        
        # If status changes to completed or failed, record completion time and calculate duration
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
        
        # Execute update
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
        """Recycle timed-out running tasks, return update count"""
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
        """Delete task"""
        stmt = delete(TaskModel).where(TaskModel.id == task_id)
        if user_id:
            stmt = stmt.where(TaskModel.user_id == user_id)
            
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0


# Create global instance
task_crud = TaskCRUD()
