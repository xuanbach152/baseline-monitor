"""Rule API router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from app.modules.websocket.service import manager
from . import crud
from .schemas import RuleCreate, RuleUpdate, RuleResponse

router = APIRouter(prefix="/rules", tags=["rules"])

@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    """
    Create a new CIS compliance rule.
    """
    return crud.create_rule(db, rule)

@router.get("/", response_model=List[RuleResponse])
def list_rules(
    skip: int = 0,
    limit: int = 100,
    active: Optional[bool] = None,
    severity: Optional[str] = None,
    os_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of rules with optional filters.
    """
    return crud.get_rules(db, skip=skip, limit=limit, active=active, severity=severity, os_type=os_type)

@router.get("/agent/{agent_rule_id}", response_model=RuleResponse)
def get_rule_by_agent_id(agent_rule_id: str, db: Session = Depends(get_db)):
    """
    Get rule by agent_rule_id (e.g., 'UBU-01', 'WIN-03').
    
    """
    rule = crud.get_rule_by_agent_id(db, agent_rule_id)
    return rule


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """
    Get rule by ID.
    """
    return crud.get_rule(db, rule_id)

@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(rule_id: int, rule_update: RuleUpdate, db: Session = Depends(get_db)):
    """
    Update rule information.
    
    """
    updated_rule = crud.update_rule(db, rule_id, rule_update)
    
    # Broadcast update
    await manager.broadcast_rule_updated({
        "id": updated_rule.id,
        "name": updated_rule.name,
        "severity": updated_rule.severity,
        "is_active": updated_rule.active
    })
    
    return updated_rule


@router.patch("/{rule_id}/toggle", response_model=RuleResponse)
async def toggle_rule_active(rule_id: int, db: Session = Depends(get_db)):
    """
    Toggle rule active/inactive status.
    """
    toggled_rule = crud.toggle_rule_active(db, rule_id)
    
    # Broadcast toggle
    await manager.broadcast_rule_toggled({
        "id": toggled_rule.id,
        "name": toggled_rule.name,
        "is_active": toggled_rule.active
    })
    
    return toggled_rule

@router.delete("/{rule_id}")
async def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """
    Delete rule.
    """
    crud.delete_rule(db, rule_id)
    
    # Broadcast deletion
    await manager.broadcast_rule_deleted(str(rule_id))
    
    return {
        "message": "Rule deleted successfully",
        "rule_id": rule_id
    }
