"""
Pydantic schemas for YamlFile entity
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class YamlFileBase(BaseModel):
    """Base YamlFile schema"""
    file_type: str = Field(..., pattern="^(agents|tasks|tools|config)$")
    filename: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    version: Optional[str] = Field(None, max_length=50)
    is_valid: bool = Field(default=True)


class YamlFileCreate(YamlFileBase):
    """Schema for creating a new YAML file"""
    project_id: str


class YamlFileUpdate(BaseModel):
    """Schema for updating a YAML file"""
    content: Optional[str] = Field(None, min_length=1)
    version: Optional[str] = Field(None, max_length=50)
    is_valid: Optional[bool] = None
    validation_errors: Optional[dict] = None


class YamlFile(YamlFileBase):
    """Schema for YAML file response"""
    id: str
    project_id: str
    validation_errors: Optional[dict] = None
    generated_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
