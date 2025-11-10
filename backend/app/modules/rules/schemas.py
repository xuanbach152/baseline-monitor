"""Rule schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional


class RuleBase(BaseModel):
    """Base rule schema."""
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    check_expression: Optional[str] = None
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")


class RuleCreate(RuleBase):
    """Schema for creating a new rule."""
    pass


class RuleUpdate(BaseModel):
    """Schema for updating rule."""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    check_expression: Optional[str] = None
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    active: Optional[bool] = None


class RuleResponse(RuleBase):
    """Schema for rule response."""
    id: int
    active: bool

    class Config:
        from_attributes = True
