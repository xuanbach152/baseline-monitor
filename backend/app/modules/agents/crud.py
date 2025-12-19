"""Agent CRUD operations."""
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status

from .models import Agent
from .schemas import AgentCreate, AgentUpdate, AgentHeartbeat


def get_agent(db: Session, agent_id: int) -> Agent:
    """Get agent by ID. Raises 404 if not found."""
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )
    return db_agent


def get_agent_by_hostname(db: Session, hostname: str) -> Optional[Agent]:
    """Get agent by hostname."""
    return db.query(Agent).filter(Agent.hostname == hostname).first()


def get_agents(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_online: Optional[bool] = None,
    os: Optional[str] = None
) -> List[Agent]:
    """Get list of agents with optional filters."""
    query = db.query(Agent)
    
    if is_online is not None:
        query = query.filter(Agent.is_online == is_online)
    
    if os:
        query = query.filter(Agent.os.ilike(f"%{os}%"))
    
    return query.offset(skip).limit(limit).all()


def create_agent(db: Session, agent: AgentCreate) -> Agent:
    """
    Register new agent or update existing one (UPSERT).
    """
    # Check if agent with this hostname already exists
    existing_agent = get_agent_by_hostname(db, agent.hostname)
    
    if existing_agent:
        # Agent exists → Update information
        existing_agent.ip_address = agent.ip_address
        existing_agent.os = agent.os
        existing_agent.version = agent.version
        existing_agent.is_online = True
        existing_agent.last_checkin = datetime.now()
        
        db.commit()
        db.refresh(existing_agent)
        return existing_agent
    
    # Agent doesn't exist → Create new
    db_agent = Agent(
        **agent.model_dump(),
        is_online=True,
        last_checkin=datetime.now()
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def update_agent(db: Session, agent_id: int, agent_update: AgentUpdate) -> Agent:
    """Update agent. Raises 404 if not found."""
    db_agent = get_agent(db, agent_id)  # ← Auto raise 404
    
    update_data = agent_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    for field, value in update_data.items():
        setattr(db_agent, field, value)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent


def delete_agent(db: Session, agent_id: int) -> None:
    """Delete agent. Raises 404 if not found."""
    db_agent = get_agent(db, agent_id)  # ← Auto raise 404
    
    db.delete(db_agent)
    db.commit()


def update_agent_heartbeat(
    db: Session,
    agent_id: int,
    heartbeat: AgentHeartbeat
) -> Agent:
    """Update agent heartbeat/keep-alive. Raises 404 if not found."""
    db_agent = get_agent(db, agent_id)  # ← Auto raise 404
    
    db_agent.last_checkin = datetime.now()
    db_agent.is_online = heartbeat.is_online
    
    if heartbeat.version:
        db_agent.version = heartbeat.version
    
    db.commit()
    db.refresh(db_agent)
    return db_agent


def get_online_agents_count(db: Session) -> int:
    """Get count of online agents."""
    return db.query(Agent).filter(Agent.is_online == True).count()


def get_total_agents_count(db: Session) -> int:
    """Get total count of agents."""
    return db.query(Agent).count()


def calculate_agent_compliance(db: Session, agent_id: int) -> float:
    """
    Calculate compliance rate for an agent.
    
    Compliance = (Total Active Rules - Unresolved Violations) / Total Active Rules * 100
    
    Returns:
        float: Compliance percentage (0-100)
    """
    from app.modules.rules.models import Rule
    from app.modules.violations.models import Violation
    
    # Get total active rules
    total_rules = db.query(Rule).filter(Rule.active == True).count()
    
    print(f"[COMPLIANCE DEBUG] Agent {agent_id}: total_rules={total_rules}")
    
    if total_rules == 0:
        return 100.0  # No rules = 100% compliant
    
    # Get unresolved violations for this agent
    unresolved_violations = db.query(Violation).filter(
        Violation.agent_id == agent_id,
        Violation.resolved_at.is_(None)
    ).count()
    
    print(f"[COMPLIANCE DEBUG] Agent {agent_id}: unresolved_violations={unresolved_violations}")
    
    # Calculate compliance rate
    compliance = max(0, (total_rules - unresolved_violations) / total_rules * 100)
    
    print(f"[COMPLIANCE DEBUG] Agent {agent_id}: compliance={compliance}")
    
    return round(compliance, 2)


def update_agent_compliance(db: Session, agent_id: int) -> Agent:
    """
    Update agent's compliance rate.
    """
    db_agent = get_agent(db, agent_id)
    db_agent.compliance_rate = calculate_agent_compliance(db, agent_id)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def update_all_agents_compliance(db: Session) -> None:
    """Update compliance rate for all agents."""
    agents = db.query(Agent).all()
    for agent in agents:
        agent.compliance_rate = calculate_agent_compliance(db, agent.id)
    db.commit()
