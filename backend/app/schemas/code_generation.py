"""
Pydantic schemas for CodeGeneration entity
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CodeGenerationBase(BaseModel):
    """Base CodeGeneration schema"""
    framework: str = Field(..., pattern="^(crewai|langchain|autogen|custom)$")
    llm_provider: Optional[str] = Field(None, max_length=50)
    status: str = Field(
        default="pending",
        pattern="^(pending|generating|ready|error|building|deploying|deployed)$"
    )


class CodeGenerationCreate(CodeGenerationBase):
    """Schema for creating a new code generation"""
    project_id: str


class CodeGenerationUpdate(BaseModel):
    """Schema for updating a code generation"""
    status: Optional[str] = Field(
        None,
        pattern="^(pending|generating|ready|error|building|deploying|deployed)$"
    )
    code_structure: Optional[dict] = None
    files: Optional[dict] = None
    deployment_url: Optional[str] = Field(None, max_length=500)
    build_logs: Optional[dict] = None
    test_results: Optional[dict] = None
    quality_metrics: Optional[dict] = None
    metadata: Optional[dict] = None


class CodeGeneration(CodeGenerationBase):
    """Schema for code generation response"""
    id: str
    project_id: str
    code_structure: Optional[dict] = None
    files: Optional[dict] = None
    generated_at: datetime
    built_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    deployment_url: Optional[str] = None
    build_logs: Optional[dict] = None
    test_results: Optional[dict] = None
    quality_metrics: Optional[dict] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
