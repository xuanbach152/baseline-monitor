"""User service layer for business logic."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from . import crud
from .schemas import UserResponse


def login_user(db: Session, username: str, password: str) -> dict:
    """
    Login user with username and password.
   
    """
    # Authenticate user (raises 401 if invalid)
    user = crud.authenticate_user(db, username, password)
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Return success response with user info
    return {
        "message": "Login successful",
        "user": UserResponse.model_validate(user)
    }
