"""
Pydantic schemas for McpConnection entity
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class McpConnectionBase(BaseModel):
    """Base McpConnection schema"""
    server_name: str = Field(..., min_length=1, max_length=255)
    server_url: str = Field(..., min_length=1, max_length=500)
    auth_type: str = Field(default="none", pattern="^(none|basic|bearer|apikey)$")
    status: str = Field(default="inactive", pattern="^(active|inactive|error)$")


class McpConnectionCreate(McpConnectionBase):
    """Schema for creating a new MCP connection"""
    project_id: Optional[str] = None
    auth_credentials: Optional[dict] = None
    services: Optional[List[str]] = None


class McpConnectionUpdate(BaseModel):
    """Schema for updating an MCP connection"""
    server_name: Optional[str] = Field(None, min_length=1, max_length=255)
    server_url: Optional[str] = Field(None, min_length=1, max_length=500)
    auth_type: Optional[str] = Field(None, pattern="^(none|basic|bearer|apikey)$")
    auth_credentials: Optional[dict] = None
    services: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|error)$")
    health_check_url: Optional[str] = Field(None, max_length=500)
    metadata: Optional[dict] = None


class McpConnection(McpConnectionBase):
    """Schema for MCP connection response"""
    id: str
    project_id: Optional[str] = None
    services: Optional[List[str]] = None
    last_sync: Optional[datetime] = None
    health_check_url: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
