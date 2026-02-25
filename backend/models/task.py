"""
Task model: stores crawler task status and results
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import uuid


class TaskModel(Base):
    """Crawler task model"""
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User association (foreign key) - ensures data isolation
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), 
                    nullable=False, index=True)
    
    # Task info
    crawler_type = Column(String(50), nullable=False, index=True)
    status = Column(
        String(20), 
        nullable=False, 
        default="pending",
        index=True
    )  # pending, running, completed, failed, cancelled
    
    # Progress
    progress = Column(Integer, default=0)  # 0-100
    
    # Input parameters (JSON string)
    params = Column(Text, nullable=True)
    
    # Result and error info
    result = Column(Text, nullable=True)  # Store result in JSON format
    error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Performance stats
    duration = Column(Float, nullable=True)  # Execution duration (seconds)
    retry_count = Column(Integer, default=0)
    
    # Relationship
    user = relationship("UserModel", back_populates="tasks")
    
    # Composite index - optimize queries
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_status_user', 'status', 'user_id'),
    )
    
    def __repr__(self):
        return f"<Task {self.id[:8]} - {self.crawler_type} - {self.status}>"
