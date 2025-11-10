"""Agent API router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from . import crud
from .schemas import AgentCreate, AgentUpdate, AgentResponse, AgentHeartbeat

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def register_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """
    Register a new agent (monitored host).
    
    - **hostname**: Server hostname
    - **ip_address**: IP address (optional)
    - **os**: Operating system (e.g., "Ubuntu 22.04")
    - **version**: Agent software version
    """
    # Check if hostname already exists
    if crud.get_agent_by_hostname(db, agent.hostname):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent with this hostname already exists"
        )
    
    return crud.create_agent(db, agent)


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
    agents = crud.get_agents(db, skip=skip, limit=limit, is_online=is_online, os=os)
    return agents


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


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """
    Get agent by ID.
    """
    db_agent = crud.get_agent(db, agent_id)
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return db_agent


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: int, agent_update: AgentUpdate, db: Session = Depends(get_db)):
    """
    Update agent information.
    
    All fields are optional. Only provided fields will be updated.
    """
    db_agent = crud.update_agent(db, agent_id, agent_update)
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return db_agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """
    Delete agent.
    """
    success = crud.delete_agent(db, agent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return None


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
    db_agent = crud.update_agent_heartbeat(db, agent_id, heartbeat)
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return db_agent
