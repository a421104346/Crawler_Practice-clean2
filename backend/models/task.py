"""
任务模型：存储爬虫任务的状态和结果
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import uuid


class TaskModel(Base):
    """爬虫任务模型"""
    __tablename__ = "tasks"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 用户关联（外键） - 确保数据隔离
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), 
                    nullable=False, index=True)
    
    # 任务信息
    crawler_type = Column(String(50), nullable=False, index=True)
    status = Column(
        String(20), 
        nullable=False, 
        default="pending",
        index=True
    )  # pending, running, completed, failed, cancelled
    
    # 进度
    progress = Column(Integer, default=0)  # 0-100
    
    # 输入参数（JSON字符串）
    params = Column(Text, nullable=True)
    
    # 结果和错误信息
    result = Column(Text, nullable=True)  # JSON格式存储结果
    error = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 性能统计
    duration = Column(Float, nullable=True)  # 执行时长（秒）
    retry_count = Column(Integer, default=0)
    
    # 关系定义
    user = relationship("UserModel", back_populates="tasks")
    
    # 复合索引 - 优化查询
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_status_user', 'status', 'user_id'),
    )
    
    def __repr__(self):
        return f"<Task {self.id[:8]} - {self.crawler_type} - {self.status}>"
