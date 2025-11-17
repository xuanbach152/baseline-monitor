"""Violation API router."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from . import crud
from .schemas import (
    ViolationCreate,
    ViolationCreateFromAgent,
    ViolationUpdate, 
    ViolationResponse,
    ViolationWithDetail,
    ViolationStats
)

router = APIRouter(prefix="/violations", tags=["violations"])


# ============================================================================
# CREATE Operations
# ============================================================================

@router.post("/", response_model=ViolationResponse, status_code=status.HTTP_201_CREATED)
def create_violation(violation: ViolationCreate, db: Session = Depends(get_db)):
    """
    Create a new violation record.
    
    - **agent_id**: ID of the agent where violation was detected
    - **rule_id**: ID of the rule that was violated (Integer)
    - **message**: Description of the violation
    - **confidence_score**: Confidence level (0.0-1.0)
    """
    return crud.create_violation(db, violation)


@router.post("/from-agent", response_model=ViolationResponse, status_code=status.HTTP_201_CREATED)
def create_violation_from_agent(violation: ViolationCreateFromAgent, db: Session = Depends(get_db)):
    """
    Create violation from agent (uses agent_rule_id instead of rule_id).
    
    Agents report violations using agent_rule_id (e.g., 'UBU-01'), 
    this endpoint converts it to backend rule_id before saving.
    
    - **agent_id**: ID of the agent
    - **agent_rule_id**: Agent-side rule ID (e.g., 'UBU-01', 'WIN-03')
    - **message**: Description of the violation
    - **confidence_score**: Confidence level (0.0-1.0)
    """
    # Lookup rule by agent_rule_id
    from app.modules.rules import crud as rules_crud
    rule = rules_crud.get_rule_by_agent_id(db, violation.agent_rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with agent_rule_id '{violation.agent_rule_id}' not found"
        )
    
    # Convert to ViolationCreate with Integer rule_id
    violation_data = ViolationCreate(
        agent_id=violation.agent_id,
        rule_id=rule.id,  # Convert agent_rule_id -> rule.id
        message=violation.message,
        confidence_score=violation.confidence_score
    )
    
    return crud.create_violation(db, violation_data)


# ============================================================================
# READ Operations - List
# ============================================================================

@router.get("/", response_model=List[ViolationResponse])
def list_violations(
    skip: int = 0,
    limit: int = 100,
    agent_id: Optional[int] = Query(None, description="Filter by agent ID"),
    rule_id: Optional[int] = Query(None, description="Filter by rule ID"),
    severity: Optional[str] = Query(None, description="Filter by severity (critical, high, medium, low)"),
    db: Session = Depends(get_db)
):
    """
    Get list of violations with optional filters.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **agent_id**: Filter by specific agent
    - **rule_id**: Filter by specific rule
    - **severity**: Filter by severity level
    """
    return crud.get_violations(
        db, 
        skip=skip, 
        limit=limit, 
        agent_id=agent_id, 
        rule_id=rule_id, 
        severity=severity
    )


# ============================================================================
# READ Operations - Special Routes (must be before /{id})
# ============================================================================

@router.get("/recent", response_model=List[ViolationResponse])
def get_recent_violations(
    hours: int = Query(24, ge=1, le=168, description="Number of hours (1-168)"),
    limit: int = Query(50, ge=1, le=200, description="Max results (1-200)"),
    db: Session = Depends(get_db)
):
    """
    Get recent violations within specified hours.
    
    - **hours**: Time window in hours (default: 24, max: 168 = 7 days)
    - **limit**: Maximum number of records to return (default: 50)
    """
    return crud.get_recent_violations(db, hours=hours, limit=limit)


@router.get("/stats", response_model=ViolationStats)
def get_violation_statistics(db: Session = Depends(get_db)):
    """
    Get comprehensive violation statistics.
    
    Returns:
    - Total violation count
    - Recent violations (24h)
    - Breakdown by severity
    - Top 5 agents with most violations
    """
    return crud.get_violation_stats(db)


@router.get("/stats/count")
def get_total_count(db: Session = Depends(get_db)):
    """Get total count of all violations."""
    return {
        "total_violations": crud.get_total_violations_count(db)
    }


@router.get("/stats/by-severity")
def get_by_severity(db: Session = Depends(get_db)):
    """
    Get violations count grouped by severity.
    
    Returns count for each severity level (critical, high, medium, low).
    """
    return crud.get_violations_count_by_severity(db)


@router.get("/stats/by-agent")
def get_by_agent(db: Session = Depends(get_db)):
    """
    Get violations count grouped by agent.
    
    Returns count for each agent with hostname.
    """
    return crud.get_violations_count_by_agent(db)


@router.get("/stats/recent-count")
def get_recent_count(
    hours: int = Query(24, ge=1, le=168, description="Number of hours (1-168)"),
    db: Session = Depends(get_db)
):
    """
    Get count of violations in the last X hours.
    
    - **hours**: Time window in hours (default: 24)
    """
    return {
        "hours": hours,
        "count": crud.get_recent_violations_count(db, hours=hours)
    }


@router.get("/agent/{agent_id}", response_model=List[ViolationResponse])
def get_violations_by_agent(
    agent_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all violations for a specific agent.
    
    - **agent_id**: ID of the agent
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    return crud.get_violations_by_agent(db, agent_id, skip=skip, limit=limit)


@router.get("/rule/{rule_id}", response_model=List[ViolationResponse])
def get_violations_by_rule(
    rule_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all violations for a specific rule.
    
    - **rule_id**: ID of the rule
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    return crud.get_violations_by_rule(db, rule_id, skip=skip, limit=limit)


# ============================================================================
# READ Operations - By ID (must be last in GET)
# ============================================================================

@router.get("/{violation_id}", response_model=ViolationResponse)
def get_violation(violation_id: int, db: Session = Depends(get_db)):
    """
    Get violation by ID.
    """
    return crud.get_violation(db, violation_id)


# ============================================================================
# UPDATE Operations
# ============================================================================

@router.put("/{violation_id}", response_model=ViolationResponse)
def update_violation(
    violation_id: int, 
    violation_update: ViolationUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update violation information.
    
    All fields are optional. Only provided fields will be updated.
    Common use case: Update message or confidence_score.
    """
    return crud.update_violation(db, violation_id, violation_update)


# ============================================================================
# DELETE Operations
# ============================================================================

@router.delete("/{violation_id}")
def delete_violation(violation_id: int, db: Session = Depends(get_db)):
    """
    Delete a single violation.
    """
    crud.delete_violation(db, violation_id)
    return {
        "message": "Violation deleted successfully",
        "violation_id": violation_id
    }


@router.delete("/agent/{agent_id}/all")
def delete_agent_violations(agent_id: int, db: Session = Depends(get_db)):
    """
    Delete all violations for a specific agent.
    
    Use case: Cleanup when unregistering an agent.
    """
    deleted_count = crud.delete_violations_by_agent(db, agent_id)
    return {
        "message": f"Deleted {deleted_count} violations for agent {agent_id}",
        "agent_id": agent_id,
        "deleted_count": deleted_count
    }
