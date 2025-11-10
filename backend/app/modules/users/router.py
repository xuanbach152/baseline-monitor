"""User API router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from . import crud
from .schemas import UserCreate, UserUpdate, UserResponse, UserLogin

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    - **username**: Unique username (3-50 chars)
    - **email**: Unique email address
    - **password**: Password (min 6 chars)
    - **role**: admin, operator, or viewer
    """
    # Check if username exists
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return crud.create_user(db, user)


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
    users = crud.get_users(db, skip=skip, limit=limit, is_active=is_active, role=role)
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID.
    """
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update user information.
    
    All fields are optional. Only provided fields will be updated.
    """
    db_user = crud.update_user(db, user_id, user_update)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete user.
    """
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint (simple version without JWT).
    
    Returns user info if credentials are valid.
    """
    user = crud.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return {
        "message": "Login successful",
        "user": UserResponse.model_validate(user)
    }
