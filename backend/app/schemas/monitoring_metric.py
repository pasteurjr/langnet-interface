"""
Pydantic schemas for MonitoringMetric entity
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class MonitoringMetricBase(BaseModel):
    """Base MonitoringMetric schema"""
    metric_type: str = Field(..., pattern="^(llm_call|token_usage|latency|error|cost)$")
    metric_name: str = Field(..., min_length=1, max_length=255)
    metric_value: Optional[Decimal] = None
    metric_unit: Optional[str] = Field(None, max_length=50)


class MonitoringMetricCreate(MonitoringMetricBase):
    """Schema for creating a new monitoring metric"""
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    task_execution_id: Optional[str] = None
    trace_id: Optional[str] = Field(None, max_length=255)
    span_id: Optional[str] = Field(None, max_length=255)
    metadata: Optional[dict] = None


class MonitoringMetric(MonitoringMetricBase):
    """Schema for monitoring metric response"""
    id: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    task_execution_id: Optional[str] = None
    timestamp: datetime
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
