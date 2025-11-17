"""
Pydantic schemas for VerboseLog entity
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class VerboseLogBase(BaseModel):
    """Base VerboseLog schema"""
    log_level: str = Field(..., pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    message: str = Field(..., min_length=1)
    source: Optional[str] = Field(None, max_length=255)


class VerboseLogCreate(VerboseLogBase):
    """Schema for creating a new verbose log"""
    task_execution_id: str
    metadata: Optional[dict] = None


class VerboseLog(VerboseLogBase):
    """Schema for verbose log response"""
    id: str
    task_execution_id: str
    timestamp: datetime
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
