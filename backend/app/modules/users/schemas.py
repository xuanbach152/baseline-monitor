"""User schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=100)  
    role: str = Field(default="viewer", pattern="^(admin|operator|viewer)$")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format (allow .local for dev/testing)."""
        # Simple email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        # Also allow .local domain for dev
        local_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.local$'
        
        if not (re.match(email_pattern, v) or re.match(local_pattern, v)):
            raise ValueError('Invalid email format')
        return v.lower()  


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, min_length=3, max_length=100)  
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    role: Optional[str] = Field(None, pattern="^(admin|operator|viewer)$")
    is_active: Optional[bool] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format if provided."""
        if v is None:
            return v
        
        # Simple email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        # Also allow .local domain for dev
        local_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.local$'
        
        if not (re.match(email_pattern, v) or re.match(local_pattern, v)):
            raise ValueError('Invalid email format')
        return v.lower()  # Normalize to lowercase


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str
