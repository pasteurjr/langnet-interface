"""
Pydantic schemas for Specification entity
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SpecificationBase(BaseModel):
    """Base Specification schema"""
    content: str = Field(..., min_length=1)
    version: str = Field(default="1.0", max_length=50)
    status: str = Field(default="draft", pattern="^(draft|generated|reviewing|approved|needs_revision)$")


class SpecificationCreate(SpecificationBase):
    """Schema for creating a new specification"""
    project_id: str
    user_id: str


class SpecificationUpdate(BaseModel):
    """Schema for updating a specification"""
    content: Optional[str] = Field(None, min_length=1)
    version: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, pattern="^(draft|generated|reviewing|approved|needs_revision)$")
    requirements_functional: Optional[dict] = None
    requirements_nonfunctional: Optional[dict] = None
    data_model: Optional[dict] = None
    workflows: Optional[dict] = None
    approved_by: Optional[str] = None


class Specification(SpecificationBase):
    """Schema for specification response"""
    id: str
    project_id: str
    user_id: str
    requirements_functional: Optional[dict] = None
    requirements_nonfunctional: Optional[dict] = None
    data_model: Optional[dict] = None
    workflows: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None

    class Config:
        from_attributes = True
