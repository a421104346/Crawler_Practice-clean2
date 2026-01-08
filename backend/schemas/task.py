"""
任务相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class TaskCreate(BaseModel):
    """创建任务的请求模型"""
    crawler_type: str = Field(..., description="爬虫类型", example="yahoo")
    params: Optional[dict] = Field(default={}, description="爬虫参数")
    user_id: Optional[str] = Field(None, description="用户ID（可选）")


class TaskUpdate(BaseModel):
    """更新任务的请求模型"""
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    result: Optional[Any] = None
    error: Optional[str] = None


class TaskResponse(BaseModel):
    """任务响应模型"""
    id: str
    crawler_type: str
    status: str
    progress: int
    params: Optional[dict] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    user_id: Optional[str] = None
    
    class Config:
        from_attributes = True  # 允许从 ORM 模型转换


class TaskListResponse(BaseModel):
    """任务列表响应"""
    total: int
    tasks: list[TaskResponse]
    page: int = 1
    page_size: int = 20
