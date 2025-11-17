"""
Pydantic schemas for Document entity
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base Document schema"""
    filename: str = Field(..., min_length=1, max_length=255)
    original_filename: str = Field(..., min_length=1, max_length=255)
    file_type: Optional[str] = Field(None, max_length=50)
    file_size: Optional[int] = None
    file_path: Optional[str] = Field(None, max_length=1000)
    storage_type: str = Field(default="local", pattern="^(local|s3|gcs|azure)$")


class DocumentCreate(DocumentBase):
    """Schema for creating a new document"""
    project_id: str
    user_id: str


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    status: Optional[str] = Field(None, pattern="^(uploaded|analyzing|analyzed|error)$")
    analysis_results: Optional[dict] = None
    extracted_entities: Optional[dict] = None
    requirements: Optional[dict] = None
    metadata: Optional[dict] = None


class Document(DocumentBase):
    """Schema for document response"""
    id: str
    project_id: str
    user_id: str
    uploaded_at: datetime
    status: str
    analysis_results: Optional[dict] = None
    extracted_entities: Optional[dict] = None
    requirements: Optional[dict] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
