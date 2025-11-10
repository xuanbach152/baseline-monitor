"""Rule API router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from . import crud
from .schemas import RuleCreate, RuleUpdate, RuleResponse

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    """
    Create a new CIS compliance rule.
    
    - **name**: Rule name (e.g., "Ensure SSH root login is disabled")
    - **description**: Detailed description
    - **check_expression**: Command/script to check compliance
    - **severity**: low, medium, high, or critical
    """
    # Check if rule name exists
    if crud.get_rule_by_name(db, rule.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rule with this name already exists"
        )
    
    return crud.create_rule(db, rule)


@router.get("/", response_model=List[RuleResponse])
def list_rules(
    skip: int = 0,
    limit: int = 100,
    active: Optional[bool] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of rules with optional filters.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **active**: Filter by active status
    - **severity**: Filter by severity (low, medium, high, critical)
    """
    rules = crud.get_rules(db, skip=skip, limit=limit, active=active, severity=severity)
    return rules


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """
    Get rule by ID.
    """
    db_rule = crud.get_rule(db, rule_id)
    if not db_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    return db_rule


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: int, rule_update: RuleUpdate, db: Session = Depends(get_db)):
    """
    Update rule information.
    
    All fields are optional. Only provided fields will be updated.
    """
    db_rule = crud.update_rule(db, rule_id, rule_update)
    if not db_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    return db_rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """
    Delete rule.
    """
    success = crud.delete_rule(db, rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    return None


@router.patch("/{rule_id}/toggle", response_model=RuleResponse)
def toggle_rule_active(rule_id: int, db: Session = Depends(get_db)):
    """
    Toggle rule active/inactive status.
    
    Quick way to enable/disable a rule without full update.
    """
    db_rule = crud.toggle_rule_active(db, rule_id)
    if not db_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    return db_rule
