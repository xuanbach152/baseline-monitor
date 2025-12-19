"""Agent API router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from app.modules.websocket.service import manager
from . import crud
from .schemas import AgentCreate, AgentUpdate, AgentResponse, AgentHeartbeat

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def register_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """
    Register a new agent (monitored host).
    """
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
    """
    return crud.get_agents(db, skip=skip, limit=limit, is_online=is_online, os=os)

@router.get("/stats")
def get_agents_stats(db: Session = Depends(get_db)):
    """
    Get agent statistics.
    
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
    return crud.get_agent(db, agent_id)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: int, agent_update: AgentUpdate, db: Session = Depends(get_db)):
    """
    Update agent information.
    
    """
    updated_agent = crud.update_agent(db, agent_id, agent_update)
    
    # Broadcast update
    await manager.broadcast_agent_updated({
        "id": updated_agent.id,
        "hostname": updated_agent.hostname,
        "ip_address": updated_agent.ip_address,
        "os": updated_agent.os,
        "version": updated_agent.version,
        "is_online": updated_agent.is_online
    })
    
    return updated_agent


@router.post("/{agent_id}/heartbeat", response_model=AgentResponse)
def agent_heartbeat(
    agent_id: int,
    heartbeat: AgentHeartbeat,
    db: Session = Depends(get_db)
):
    return crud.update_agent_heartbeat(db, agent_id, heartbeat)


@router.get("/{agent_id}/violations")
def get_agent_violations(
    agent_id: int,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get violations for specific agent (alias route).
    """
    from app.modules.violations import crud as violations_crud
    return violations_crud.get_violations_by_agent(db, agent_id, limit=limit)


@router.delete("/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """
    Delete agent.
    """
    crud.delete_agent(db, agent_id)
    
    # Broadcast deletion
    await manager.broadcast_agent_deleted(str(agent_id))
    
    return {
        "message": "Agent deleted successfully",
        "agent_id": agent_id
    }
