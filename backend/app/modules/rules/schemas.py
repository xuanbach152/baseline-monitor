"""Rule schemas for request/response validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class RuleBase(BaseModel):
    """Base rule schema."""
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    check_expression: Optional[str] = None
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    agent_rule_id: Optional[str] = Field(None, max_length=20, description="Agent-side rule ID (e.g., UBU-01, WIN-03)")


class RuleCreate(RuleBase):
    """Schema for creating a new rule."""
    pass


class RuleUpdate(BaseModel):
    """Schema for updating rule."""
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    check_expression: Optional[str] = None
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    active: Optional[bool] = None
    agent_rule_id: Optional[str] = Field(None, max_length=20, description="Agent-side rule ID")


class RuleResponse(RuleBase):
    """Schema for rule response."""
    id: int
    active: bool

    model_config = ConfigDict(from_attributes=True)
