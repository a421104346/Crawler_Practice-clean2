"""
Task-related Pydantic models
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime


class TaskCreate(BaseModel):
    """Task creation request model"""
    crawler_type: str = Field(
        ...,
        description="Crawler type",
        json_schema_extra={"example": "yahoo"}
    )
    params: Optional[dict] = Field(default={}, description="Crawler parameters")
    user_id: Optional[str] = Field(None, description="User ID (optional)")


class TaskUpdate(BaseModel):
    """Task update request model"""
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    result: Optional[Any] = None
    error: Optional[str] = None


class TaskResponse(BaseModel):
    """Task response model"""
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
    
    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Task list response"""
    total: int
    tasks: list[TaskResponse]
    page: int = 1
    page_size: int = 20
    total_pages: int = 1
