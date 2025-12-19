"""Violation schemas for request/response validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ViolationBase(BaseModel):
    """Base violation schema """
    model_config = ConfigDict(extra="forbid")
    agent_id: int = Field(..., description="ID của agent bị vi phạm")
    rule_id: int = Field(..., description="ID của CIS rule bị vi phạm")
    message: str = Field(..., description="Mô tả chi tiết violation")
    confidence_score: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Độ tin cậy (0.0-1.0), mặc định 1.0"
    )


class ViolationCreate(ViolationBase):
    """Schema for creating/registering a new violation."""
    pass


class ViolationCreateFromAgent(BaseModel):
    """Schema for agent reporting violations (uses agent_rule_id instead of rule_id)."""
    model_config = ConfigDict(extra="forbid")
    agent_id: int = Field(..., description="ID của agent")
    agent_rule_id: str = Field(..., description="Agent-side rule ID (e.g., 'UBU-01')")
    message: str = Field(..., description="Mô tả chi tiết violation")
    confidence_score: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Độ tin cậy (0.0-1.0)"
    )


class ViolationUpdate(BaseModel):
    """Schema for updating violation."""
    model_config = ConfigDict(extra="forbid")
    message: Optional[str] = Field(None, description="Update mô tả violation")
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Update độ tin cậy"
    )
    resolved_at: Optional[datetime] = Field(None, description="Thời gian resolved")
    resolved_by: Optional[str] = Field(None, description="User đã resolve")
    resolution_notes: Optional[str] = Field(None, description="Ghi chú khi resolve")
    

class ViolationResponse(ViolationBase):
    """Schema for violation response."""
    id: int = Field(..., description="Violation ID")
    detected_at: datetime = Field(..., description="Thời điểm phát hiện violation")
    resolved_at: Optional[datetime] = Field(None, description="Thời gian resolved")
    resolved_by: Optional[str] = Field(None, description="User đã resolve")
    resolution_notes: Optional[str] = Field(None, description="Ghi chú khi resolve")
    
    class Config:
        from_attributes = True 

class ViolationWithDetail(ViolationBase):
    """Schema for violation detail"""
    id: int = Field(..., description="Violation ID")
    detected_at: datetime = Field(..., description="Thời điểm phát hiện violation")
    resolved_at: Optional[datetime] = Field(None, description="Thời gian resolved")
    resolved_by: Optional[str] = Field(None, description="User đã resolve")
    resolution_notes: Optional[str] = Field(None, description="Ghi chú khi resolve")
    agent: Optional[dict] = Field(
        None,
        description="Nested agent details: {id, hostname, ip_address, os, is_online}"
    )
    rule: Optional[dict] = Field(
        None,
        description="Nested rule details: {id, name, severity, description}"
    )
    class Config:
        from_attributes = True 

class ViolationStats(BaseModel):
    """Schema for comprehensive violation statistics."""
    total_violations: int = Field(..., description="Tổng số violations trong hệ thống")
    recent_violations_24h: int = Field(..., description="Violations phát hiện trong 24h qua")
    by_severity: dict = Field(
        ...,
        description="Phân loại theo severity: {critical: 50, high: 120, medium: 30, low: 0}"
    )
    top_5_agents: list = Field(
        ...,
        description="Top 5 agents có nhiều violations nhất: [{agent_id, hostname, violation_count}, ...]"
    )

