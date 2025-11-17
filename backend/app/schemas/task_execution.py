"""
Pydantic schemas for TaskExecution entity
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskExecutionBase(BaseModel):
    """Base TaskExecution schema"""
    task_name: str = Field(..., min_length=1, max_length=255)
    agent_name: Optional[str] = Field(None, max_length=255)
    status: str = Field(
        default="pending",
        pattern="^(pending|running|completed|failed|skipped)$"
    )


class TaskExecutionCreate(TaskExecutionBase):
    """Schema for creating a new task execution"""
    session_id: str
    input_data: Optional[dict] = None


class TaskExecutionUpdate(BaseModel):
    """Schema for updating a task execution"""
    status: Optional[str] = Field(
        None,
        pattern="^(pending|running|completed|failed|skipped)$"
    )
    output_data: Optional[dict] = None
    error_message: Optional[str] = None
    tokens_used: Optional[int] = Field(None, ge=0)
    execution_time_ms: Optional[int] = Field(None, ge=0)
    metadata: Optional[dict] = None


class TaskExecution(TaskExecutionBase):
    """Schema for task execution response"""
    id: str
    session_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    execution_time_ms: Optional[int] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
