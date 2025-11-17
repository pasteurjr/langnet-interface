"""
Pydantic schemas for ExecutionSession entity
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ExecutionSessionBase(BaseModel):
    """Base ExecutionSession schema"""
    status: str = Field(
        default="running",
        pattern="^(pending|running|completed|failed|cancelled)$"
    )


class ExecutionSessionCreate(ExecutionSessionBase):
    """Schema for creating a new execution session"""
    project_id: str
    user_id: str
    trigger_type: Optional[str] = Field(None, max_length=50)
    config: Optional[dict] = None


class ExecutionSessionUpdate(BaseModel):
    """Schema for updating an execution session"""
    status: Optional[str] = Field(
        None,
        pattern="^(pending|running|completed|failed|cancelled)$"
    )
    error_message: Optional[str] = None
    results: Optional[dict] = None
    metrics: Optional[dict] = None


class ExecutionSession(ExecutionSessionBase):
    """Schema for execution session response"""
    id: str
    project_id: str
    user_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    trigger_type: Optional[str] = None
    error_message: Optional[str] = None
    results: Optional[dict] = None
    metrics: Optional[dict] = None
    config: Optional[dict] = None

    class Config:
        from_attributes = True
