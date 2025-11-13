"""User API router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from . import crud, service
from .schemas import UserCreate, UserUpdate, UserResponse, UserLogin

router = APIRouter(prefix="/users", tags=["users"])


# ============================================================================
# CREATE Operations
# ============================================================================

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    - **username**: Unique username (3-50 chars)
    - **email**: Unique email address
    - **password**: Password (min 6 chars)
    - **role**: admin, operator, or viewer
    """
    return crud.create_user(db, user)


# ============================================================================
# READ Operations - List
# ============================================================================

@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of users with optional filters.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **is_active**: Filter by active status
    - **role**: Filter by role (admin, operator, viewer)
    """
    return crud.get_users(db, skip=skip, limit=limit, is_active=is_active, role=role)


# ============================================================================
# READ Operations - By ID (must be last in GET)
# ============================================================================

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID.
    """
    return crud.get_user(db, user_id)


# ============================================================================
# UPDATE Operations
# ============================================================================

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update user information.
    
    All fields are optional. Only provided fields will be updated.
    """
    return crud.update_user(db, user_id, user_update)


# ============================================================================
# DELETE Operations
# ============================================================================

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete user.
    """
    crud.delete_user(db, user_id)
    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }


# ============================================================================
# Special Operations
# ============================================================================

@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint (simple version without JWT).
    
    Returns user info if credentials are valid.
    """
    return service.login_user(db, credentials.username, credentials.password)
