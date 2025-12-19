"""Agent schemas for request/response validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class AgentBase(BaseModel):
    """Base agent schema."""
    model_config = ConfigDict(extra="forbid")
    
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)  # IPv4/IPv6
    os: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=50)


class AgentCreate(AgentBase):
    """Schema for creating/registering a new agent."""
    pass


class AgentUpdate(BaseModel):
    """Schema for updating agent."""
    model_config = ConfigDict(extra="forbid")
    
    hostname: Optional[str] = Field(None, min_length=1, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)
    os: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=50)
    is_online: Optional[bool] = None


class AgentResponse(AgentBase):
    """Schema for agent response."""
    id: int
    is_online: bool
    last_checkin: datetime
    compliance_rate: Optional[float] = None
    last_scan_at: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AgentHeartbeat(BaseModel):
    """Schema for agent heartbeat (keep-alive signal)."""
    model_config = ConfigDict(extra="forbid")
    
    version: Optional[str] = None
    is_online: bool = True
