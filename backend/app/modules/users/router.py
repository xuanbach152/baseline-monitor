"""User API router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from . import crud, service
from .schemas import UserCreate, UserUpdate, UserResponse, UserLogin

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
   
    """
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
    
    """
    return crud.get_users(db, skip=skip, limit=limit, is_active=is_active, role=role)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID.
    """
    return crud.get_user(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update user information.
    
    """
    return crud.update_user(db, user_id, user_update)


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


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint (simple version without JWT).
    
   
    """
    return service.login_user(db, credentials.username, credentials.password)
