"""Agent utility functions."""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from .models import Agent


async def mark_stale_agents_offline(db: Session, timeout_minutes: int = 5):
    """
    Mark agents as offline if they haven't sent heartbeat for X minutes.
    """
    from app.modules.websocket.service import manager
    
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
    current_time = datetime.now(timezone.utc)
    
    
    all_agents = db.query(Agent).filter(Agent.is_online == True).all()
    print(f"Checking {len(all_agents)} online agents for timeout (cutoff: {cutoff_time})")
    for a in all_agents:
        time_diff = (current_time - a.last_checkin).total_seconds() if a.last_checkin else 999
        print(f"  • {a.hostname} (ID:{a.id}) - Last checkin: {a.last_checkin} ({time_diff:.1f}s ago)")
    
    stale_agents = db.query(Agent)\
        .filter(Agent.is_online == True)\
        .filter(Agent.last_checkin < cutoff_time)\
        .all()
    
    count = 0
    for agent in stale_agents:
        agent.is_online = False
        count += 1
        print(f"Marking {agent.hostname} (ID:{agent.id}) as OFFLINE - Last checkin: {agent.last_checkin}")
        
        
        await manager.broadcast_agent_status_changed({
            "id": agent.id,
            "hostname": agent.hostname,
            "is_online": False,
            "reason": "timeout"
        })
    
    if count > 0:
        db.commit()
    
    return count
