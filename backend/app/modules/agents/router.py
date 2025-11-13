"""Agent API router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from . import crud
from .schemas import AgentCreate, AgentUpdate, AgentResponse, AgentHeartbeat

router = APIRouter(prefix="/agents", tags=["agents"])


# ============================================================================
# CREATE Operations
# ============================================================================

@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def register_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """
    Register a new agent (monitored host).
    
    - **hostname**: Server hostname
    - **ip_address**: IP address (optional)
    - **os**: Operating system (e.g., "Ubuntu 22.04")
    - **version**: Agent software version
    """
    return crud.create_agent(db, agent)


# ============================================================================
# READ Operations - List
# ============================================================================

@router.get("/", response_model=List[AgentResponse])
def list_agents(
    skip: int = 0,
    limit: int = 100,
    is_online: Optional[bool] = None,
    os: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of agents with optional filters.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **is_online**: Filter by online status
    - **os**: Filter by OS (partial match)
    """
    return crud.get_agents(db, skip=skip, limit=limit, is_online=is_online, os=os)


# ============================================================================
# READ Operations - Special Routes (must be before /{id})
# ============================================================================

@router.get("/stats")
def get_agents_stats(db: Session = Depends(get_db)):
    """
    Get agent statistics.
    
    Returns total count and online count.
    """
    return {
        "total": crud.get_total_agents_count(db),
        "online": crud.get_online_agents_count(db),
        "offline": crud.get_total_agents_count(db) - crud.get_online_agents_count(db)
    }


# ============================================================================
# READ Operations - By ID (must be last in GET)
# ============================================================================

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """
    Get agent by ID.
    """
    return crud.get_agent(db, agent_id)


# ============================================================================
# UPDATE Operations
# ============================================================================

@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: int, agent_update: AgentUpdate, db: Session = Depends(get_db)):
    """
    Update agent information.
    
    All fields are optional. Only provided fields will be updated.
    """
    return crud.update_agent(db, agent_id, agent_update)


@router.post("/{agent_id}/heartbeat", response_model=AgentResponse)
def agent_heartbeat(
    agent_id: int,
    heartbeat: AgentHeartbeat,
    db: Session = Depends(get_db)
):
    """
    Agent heartbeat endpoint (keep-alive signal).
    
    Agents should call this periodically to update online status and last_checkin time.
    """
    return crud.update_agent_heartbeat(db, agent_id, heartbeat)


# ============================================================================
# DELETE Operations
# ============================================================================

@router.delete("/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """
    Delete agent.
    """
    crud.delete_agent(db, agent_id)
    
    return {
        "message": "Agent deleted successfully",
        "agent_id": agent_id
    }
