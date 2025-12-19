"""Violation API router."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger

from app.core.dependencies import get_db
from app.modules.websocket.service import manager
from app.modules.agents import crud as agents_crud
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


@router.post("/", response_model=ViolationResponse, status_code=status.HTTP_201_CREATED)
async def create_violation(violation: ViolationCreate, db: Session = Depends(get_db)):
    """
    Create a new violation record.
    """
    new_violation = crud.create_violation(db, violation)
  
    from app.modules.agents import crud as agents_crud
    try:
        logger.info(f"Updating compliance for agent {new_violation.agent_id}")
        agents_crud.update_agent_compliance(db, new_violation.agent_id)
        logger.info(f"Compliance updated successfully")
    except Exception as e:
        # Log but don't fail the request
        logger.error(f"Failed to update agent compliance: {e}")
    
    await manager.broadcast_violation_created({
        "id": new_violation.id,
        "agent_id": new_violation.agent_id,
        "rule_id": new_violation.rule_id,
        "message": new_violation.message,
        "confidence_score": new_violation.confidence_score,
        "detected_at": new_violation.detected_at.isoformat() if new_violation.detected_at else None
    })
    
    return new_violation


@router.post("/from-agent", response_model=ViolationResponse, status_code=status.HTTP_201_CREATED)
def create_violation_from_agent(violation: ViolationCreateFromAgent, db: Session = Depends(get_db)):
    """
    Create violation from agent (uses agent_rule_id instead of rule_id).
    """
    from app.modules.rules import crud as rules_crud
    rule = rules_crud.get_rule_by_agent_id(db, violation.agent_rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with agent_rule_id '{violation.agent_rule_id}' not found"
        )
    
    violation_data = ViolationCreate(
        agent_id=violation.agent_id,
        rule_id=rule.id, 
        message=violation.message,
        confidence_score=violation.confidence_score
    )
    
    return crud.create_violation(db, violation_data)


@router.post("/agents/{agent_id}/violations/bulk")
def create_violations_bulk(
    agent_id: int,
    violations_data: dict,
    db: Session = Depends(get_db)
):
    """
    Bulk create violations from agent.
    
    - **agent_id**: ID of the agent reporting violations
    - **violations_data**: Dict with 'violations' list containing violation reports
    
    Returns count of successfully created violations.
    """
    from app.modules.rules import crud as rules_crud
    
    violations_list = violations_data.get('violations', [])
    
    if not violations_list:
        return {"message": "No violations to create", "created_count": 0}
    
    created_count = 0
    errors = []
    
    for idx, vio in enumerate(violations_list):
        try:
            # Lookup rule by agent_rule_id or rule_id
            rule_id = vio.get('rule_id')
            agent_rule_id = vio.get('agent_rule_id')
            
            if agent_rule_id:
                try:
                    rule = rules_crud.get_rule_by_agent_id(db, agent_rule_id)
                    rule_id = rule.id
                except HTTPException:
                    errors.append(f"Violation {idx}: Rule '{agent_rule_id}' not found")
                    continue
            
            if not rule_id:
                errors.append(f"Violation {idx}: Missing rule_id or agent_rule_id")
                continue
            
            # Create violation
            violation_data = ViolationCreate(
                agent_id=vio.get('agent_id', agent_id),
                rule_id=rule_id,
                message=vio.get('message', 'Violation detected'),
                confidence_score=vio.get('confidence_score', 1.0)
            )
            
            crud.create_violation(db, violation_data)
            created_count += 1
            
        except Exception as e:
            errors.append(f"Violation {idx}: {str(e)}")
            continue
    
    return {
        "message": f"Created {created_count}/{len(violations_list)} violations",
        "created_count": created_count,
        "total_submitted": len(violations_list),
        "errors": errors if errors else None
    }



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
    
    """
    return crud.get_violations(
        db, 
        skip=skip, 
        limit=limit, 
        agent_id=agent_id, 
        rule_id=rule_id, 
        severity=severity
    )

@router.get("/recent", response_model=List[ViolationResponse])
def get_recent_violations(
    hours: int = Query(24, ge=1, le=168, description="Number of hours (1-168)"),
    limit: int = Query(50, ge=1, le=200, description="Max results (1-200)"),
    db: Session = Depends(get_db)
):
    """
    Get recent violations within specified hours.
    """
    return crud.get_recent_violations(db, hours=hours, limit=limit)


@router.get("/stats", response_model=ViolationStats)
def get_violation_statistics(db: Session = Depends(get_db)):
    """
    Get comprehensive violation statistics.
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
    
    """
    return crud.get_violations_count_by_agent(db)


@router.get("/stats/recent-count")
def get_recent_count(
    hours: int = Query(24, ge=1, le=168, description="Number of hours (1-168)"),
    db: Session = Depends(get_db)
):
    """
    Get count of violations in the last X hours.

    """
    return {
        "hours": hours,
        "count": crud.get_recent_violations_count(db, hours=hours)
    }


@router.get("/stats/7day-trend")
def get_7day_trend(db: Session = Depends(get_db)):
    """
    Get 7-day violation trend (count per day for last 7 days).
    """
    return crud.get_7day_trend(db)


@router.get("/stats/top-5-recent", response_model=List[ViolationResponse])
def get_top_5_recent(db: Session = Depends(get_db)):
    """
    Get top 5 most recent violations.
    
    """
    return crud.get_top_5_recent_violations(db)


@router.get("/agent/{agent_id}", response_model=List[ViolationResponse])
def get_violations_by_agent(
    agent_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all violations for a specific agent.
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
    """
    return crud.get_violations_by_rule(db, rule_id, skip=skip, limit=limit)


@router.get("/{violation_id}", response_model=ViolationResponse)
def get_violation(violation_id: int, db: Session = Depends(get_db)):
    """
    Get violation by ID.
    """
    return crud.get_violation(db, violation_id)

@router.put("/{violation_id}", response_model=ViolationResponse)
async def update_violation(
    violation_id: int, 
    violation_update: ViolationUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update violation information.
    
    """
    updated_violation = crud.update_violation(db, violation_id, violation_update)
    
    # Update agent compliance after resolution
    try:
        agents_crud.update_agent_compliance(db, updated_violation.agent_id)
    except Exception as e:
        logger.warning(f"Failed to update agent compliance: {str(e)}")
    
    # If resolved, broadcast resolution event
    if violation_update.resolved_at or violation_update.resolved_by:
        await manager.broadcast_violation_resolved({
            "id": updated_violation.id,
            "resolved_at": updated_violation.resolved_at.isoformat() if updated_violation.resolved_at else None,
            "resolved_by": updated_violation.resolved_by,
            "resolution_notes": updated_violation.resolution_notes
        })
    
    return updated_violation

@router.delete("/{violation_id}")
async def delete_violation(violation_id: int, db: Session = Depends(get_db)):
    """
    Delete a single violation.
    """
    # Get violation first to retrieve agent_id before deletion
    violation = crud.get_violation(db, violation_id)
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    agent_id = violation.agent_id
    
    crud.delete_violation(db, violation_id)
    
    # Update agent compliance after deletion
    try:
        agents_crud.update_agent_compliance(db, agent_id)
    except Exception as e:
        logger.warning(f"Failed to update agent compliance: {str(e)}")
    
    # Broadcast deletion
    await manager.broadcast_violation_deleted(str(violation_id))
    
    return {
        "message": "Violation deleted successfully",
        "violation_id": violation_id
    }


@router.delete("/agent/{agent_id}/all")
def delete_agent_violations(agent_id: int, db: Session = Depends(get_db)):
    """
    Delete all violations for a specific agent.
    """
    deleted_count = crud.delete_violations_by_agent(db, agent_id)
    return {
        "message": f"Deleted {deleted_count} violations for agent {agent_id}",
        "agent_id": agent_id,
        "deleted_count": deleted_count
    }
