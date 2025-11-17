"""
Pydantic schemas for Task entity
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Base Task schema"""
    task_id: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    expected_output: Optional[str] = None
    async_execution: bool = Field(default=False)


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    project_id: str
    agent_id: Optional[str] = None
    tools: Optional[List[str]] = None
    context: Optional[List[str]] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    task_id: Optional[str] = Field(None, min_length=1, max_length=255)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    agent_id: Optional[str] = None
    expected_output: Optional[str] = None
    tools: Optional[List[str]] = None
    async_execution: Optional[bool] = None
    context: Optional[List[str]] = None
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    metadata: Optional[dict] = None


class Task(TaskBase):
    """Schema for task response"""
    id: str
    project_id: str
    agent_id: Optional[str] = None
    tools: Optional[List[str]] = None
    context: Optional[List[str]] = None
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
