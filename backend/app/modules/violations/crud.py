"""Violation CRUD operations."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from .models import Violation
from .schemas import ViolationCreate, ViolationUpdate
from app.modules.rules.models import Rule
from app.modules.agents.models import Agent


def get_violation(db: Session, violation_id: int) -> Violation:
    """Get violation by ID. Raises 404 if not found."""
    db_violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not db_violation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Violation with id {violation_id} not found"
        )
    return db_violation


def get_violations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    agent_id: int = None,
    rule_id: int = None,
    severity: str = None
) -> List[Violation]:
    """Get list of violations with optional filters."""
    query = db.query(Violation)
    
    if agent_id is not None:
        query = query.filter(Violation.agent_id == agent_id)
    
    if rule_id is not None:
        query = query.filter(Violation.rule_id == rule_id)
    
    if severity:
        # Join with Rule to filter by severity
        query = query.join(Rule).filter(Rule.severity == severity)
    
    return query.offset(skip).limit(limit).all()


def get_violations_by_agent(
    db: Session,
    agent_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Violation]:
    """Get violations by agent."""
    return db.query(Violation)\
        .filter(Violation.agent_id == agent_id)\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_violations_by_rule(
    db: Session,
    rule_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Violation]:
    """Get violations by rule."""
    return db.query(Violation)\
        .filter(Violation.rule_id == rule_id)\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_recent_violations(
    db: Session,
    hours: int = 24,
    limit: int = 50
) -> List[Violation]:
    """Get recent violations within specified hours."""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    return db.query(Violation)\
        .filter(Violation.detected_at >= cutoff_time)\
        .order_by(Violation.detected_at.desc())\
        .limit(limit)\
        .all()


def create_violation(db: Session, violation: ViolationCreate) -> Violation:
    """Create new violation. Validates agent and rule exist."""
    # Validate agent exists
    from app.modules.agents.crud import get_agent
    try:
        get_agent(db, violation.agent_id)  # Will raise 404 if not found
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent with id {violation.agent_id} not found"
        )
    
    # Validate rule exists
    from app.modules.rules.crud import get_rule
    try:
        get_rule(db, violation.rule_id)  # Will raise 404 if not found
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rule with id {violation.rule_id} not found"
        )
    
    # Create violation
    db_violation = Violation(**violation.model_dump())
    db.add(db_violation)
    db.commit()
    db.refresh(db_violation)
    return db_violation


def update_violation(
    db: Session,
    violation_id: int,
    violation_update: ViolationUpdate
) -> Violation:
    """Update violation. Raises 404 if not found."""
    db_violation = get_violation(db, violation_id)  # ← Auto raise 404
    
    update_data = violation_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    for field, value in update_data.items():
        setattr(db_violation, field, value)
    
    db.commit()
    db.refresh(db_violation)
    return db_violation


def delete_violation(db: Session, violation_id: int) -> None:
    """Delete violation. Raises 404 if not found."""
    db_violation = get_violation(db, violation_id)
    db.delete(db_violation)
    db.commit()



def delete_violations_by_agent(db: Session, agent_id: int) -> int:
    """Delete all violations for a specific agent. Returns count."""
    deleted_count = db.query(Violation)\
        .filter(Violation.agent_id == agent_id)\
        .delete(synchronize_session=False)
    db.commit()
    return deleted_count

def get_total_violations_count(db: Session) -> int:
    """Get total count of violations."""
    return db.query(Violation).count()


def get_violations_count_by_severity(db: Session) -> dict:
    """Get violations count grouped by severity."""
    results = db.query(
        Rule.severity,
        func.count(Violation.id).label('count')
    ).join(Rule, Violation.rule_id == Rule.id)\
     .group_by(Rule.severity)\
     .all()
    
    # Convert to dict
    severity_counts = {severity: count for severity, count in results}
    
    # Ensure all severity levels are present (with 0 if no violations)
    all_severities = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    all_severities.update(severity_counts)
    
    return all_severities


def get_violations_count_by_agent(db: Session) -> dict:
    """Get violations count grouped by agent with hostname."""
    result = db.query(
        Violation.agent_id,
        Agent.hostname,  
        func.count(Violation.id).label('count')
    ).join(Agent, Violation.agent_id == Agent.id)\
     .group_by(Violation.agent_id, Agent.hostname)\
     .all()
    
    # Return với hostname
    return {
        f"{hostname} (ID:{agent_id})": count 
        for agent_id, hostname, count in result
    }


def get_recent_violations_count(db: Session, hours: int = 24) -> int:
    """Get count of violations in the last X hours."""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    return db.query(Violation)\
        .filter(Violation.detected_at >= cutoff_time)\
        .count()



def get_violation_stats(db: Session) -> dict:
    """Get comprehensive violation statistics."""
    # Total count
    total_count = get_total_violations_count(db)
    
    # Breakdown by severity
    severity_counts = get_violations_count_by_severity(db)
    
    # Recent violations (last 24 hours)
    recent_count = get_recent_violations_count(db, hours=24)
    
    # Top 5 agents with most violations
    top_agents = db.query(
        Violation.agent_id,
        Agent.hostname,
        func.count(Violation.id).label('count')
    ).join(Agent, Violation.agent_id == Agent.id)\
     .group_by(Violation.agent_id, Agent.hostname)\
     .order_by(func.count(Violation.id).desc())\
     .limit(5)\
     .all()
    
    # Format top agents
    top_agents_list = [
        {
            "agent_id": agent_id,
            "hostname": hostname,
            "violation_count": count
        }
        for agent_id, hostname, count in top_agents
    ]
    
    # Return comprehensive stats
    return {
        "total_violations": total_count,
        "recent_violations_24h": recent_count,
        "by_severity": severity_counts,
        "top_5_agents": top_agents_list
    }

