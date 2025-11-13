"""User service layer for business logic."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from . import crud
from .schemas import UserResponse


def login_user(db: Session, username: str, password: str) -> dict:
    """
    Login user with username and password.
    
    Validates credentials and active status.
    Returns user info if successful.
    
    Raises:
        - 401: Invalid credentials
        - 403: User account is inactive
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
