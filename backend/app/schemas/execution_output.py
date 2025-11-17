"""
Pydantic schemas for ExecutionOutput entity
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ExecutionOutputBase(BaseModel):
    """Base ExecutionOutput schema"""
    output_type: str = Field(..., pattern="^(final|intermediate|error|log)$")
    content: str = Field(..., min_length=1)


class ExecutionOutputCreate(ExecutionOutputBase):
    """Schema for creating a new execution output"""
    session_id: str
    task_execution_id: Optional[str] = None
    metadata: Optional[dict] = None


class ExecutionOutput(ExecutionOutputBase):
    """Schema for execution output response"""
    id: str
    session_id: str
    task_execution_id: Optional[str] = None
    timestamp: datetime
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
