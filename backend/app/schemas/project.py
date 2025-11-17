"""
Pydantic schemas for Project entity
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base Project schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    domain: Optional[str] = Field(None, max_length=100)
    framework: Optional[str] = Field(None, pattern="^(crewai|langchain|autogen|custom)$")
    default_llm: Optional[str] = Field(None, max_length=100)
    memory_system: Optional[str] = Field(None, max_length=100)
    start_from: Optional[str] = Field("blank", pattern="^(blank|template)$")
    template: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field("draft", pattern="^(draft|active|completed|archived|error)$")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    user_id: str


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    domain: Optional[str] = Field(None, max_length=100)
    framework: Optional[str] = Field(None, pattern="^(crewai|langchain|autogen|custom)$")
    default_llm: Optional[str] = Field(None, max_length=100)
    memory_system: Optional[str] = Field(None, max_length=100)
    start_from: Optional[str] = Field(None, pattern="^(blank|template)$")
    template: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, pattern="^(draft|active|completed|archived|error)$")
    project_data: Optional[dict] = None
    petri_net: Optional[dict] = None
    config: Optional[dict] = None


class Project(ProjectBase):
    """Schema for project response"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    last_modified_by: Optional[str] = None
    project_data: Optional[dict] = None
    petri_net: Optional[dict] = None
    config: Optional[dict] = None

    class Config:
        from_attributes = True
