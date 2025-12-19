"""Rule CRUD operations."""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

from .models import Rule
from .schemas import RuleCreate, RuleUpdate


def get_rule(db: Session, rule_id: int) -> Rule:
    """Get rule by ID. Raises 404 if not found."""
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id {rule_id} not found"
        )
    return db_rule


def get_rule_by_name(db: Session, name: str) -> Optional[Rule]:
    """Get rule by name."""
    return db.query(Rule).filter(Rule.name == name).first()


def get_rule_by_agent_id(db: Session, agent_rule_id: str) -> Optional[Rule]:
    """Get rule by agent_rule_id (e.g., 'UBU-01', 'WIN-03')."""
    rule=db.query(Rule).filter(Rule.agent_rule_id == agent_rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with agent_rule_id '{agent_rule_id}' not found"
        )
    return rule


def get_rules(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active: Optional[bool] = None,
    severity: Optional[str] = None,
    os_type: Optional[str] = None
) -> List[Rule]:
    """Get list of rules with optional filters."""
    query = db.query(Rule)
    
    if active is not None:
        query = query.filter(Rule.active == active)
    
    if severity:
        query = query.filter(Rule.severity == severity)
    
    if os_type:
        query = query.filter(Rule.os_type == os_type)
    
    return query.offset(skip).limit(limit).all()


def create_rule(db: Session, rule: RuleCreate) -> Rule:
    """Create new rule. Raises 400 if rule name already exists."""
    # Check if rule name exists
    if get_rule_by_name(db, rule.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rule with this name already exists"
        )
    
    db_rule = Rule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


def update_rule(db: Session, rule_id: int, rule_update: RuleUpdate) -> Rule:
    """Update rule. Raises 404 if not found."""
    db_rule = get_rule(db, rule_id)  # ← Auto raise 404
    
    update_data = rule_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    for field, value in update_data.items():
        setattr(db_rule, field, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule


def delete_rule(db: Session, rule_id: int) -> None:
    """Delete rule. Raises 404 if not found."""
    db_rule = get_rule(db, rule_id)  # ← Auto raise 404
    
    db.delete(db_rule)
    db.commit()


def toggle_rule_active(db: Session, rule_id: int) -> Rule:
    """Toggle rule active status. Raises 404 if not found."""
    db_rule = get_rule(db, rule_id)  # ← Auto raise 404
    
    db_rule.active = not db_rule.active
    db.commit()
    db.refresh(db_rule)
    return db_rule

