"""
Pydantic schemas for Agent entity
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    """Base Agent schema"""
    agent_id: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    role: Optional[str] = Field(None, max_length=500)
    goal: Optional[str] = None
    backstory: Optional[str] = None
    verbose: bool = Field(default=False)
    allow_delegation: bool = Field(default=False)
    max_iter: int = Field(default=25, gt=0)
    max_rpm: Optional[int] = Field(None, gt=0)
    status: str = Field(default="draft", pattern="^(active|inactive|draft)$")


class AgentCreate(AgentBase):
    """Schema for creating a new agent"""
    project_id: str
    tools: Optional[List[str]] = None


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    agent_id: Optional[str] = Field(None, min_length=1, max_length=255)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = Field(None, max_length=500)
    goal: Optional[str] = None
    backstory: Optional[str] = None
    tools: Optional[List[str]] = None
    verbose: Optional[bool] = None
    allow_delegation: Optional[bool] = None
    max_iter: Optional[int] = Field(None, gt=0)
    max_rpm: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, pattern="^(active|inactive|draft)$")
    metadata: Optional[dict] = None


class Agent(AgentBase):
    """Schema for agent response"""
    id: str
    project_id: str
    tools: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
