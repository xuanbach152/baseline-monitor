"""Agent CRUD operations."""
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional, List
from datetime import datetime

from .models import Agent
from .schemas import AgentCreate, AgentUpdate, AgentHeartbeat


def get_agent(db: Session, agent_id: int) -> Optional[Agent]:
    """Get agent by ID."""
    return db.query(Agent).filter(Agent.id == agent_id).first()


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
    """Create/register new agent."""
    db_agent = Agent(**agent.model_dump(), is_online=True)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def update_agent(db: Session, agent_id: int, agent_update: AgentUpdate) -> Optional[Agent]:
    """Update agent."""
    db_agent = get_agent(db, agent_id)
    if not db_agent:
        return None
    
    update_data = agent_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_agent, field, value)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent


def delete_agent(db: Session, agent_id: int) -> bool:
    """Delete agent."""
    db_agent = get_agent(db, agent_id)
    if not db_agent:
        return False
    
    db.delete(db_agent)
    db.commit()
    return True


def update_agent_heartbeat(
    db: Session,
    agent_id: int,
    heartbeat: AgentHeartbeat
) -> Optional[Agent]:
    """Update agent heartbeat/keep-alive."""
    db_agent = get_agent(db, agent_id)
    if not db_agent:
        return None
    
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
