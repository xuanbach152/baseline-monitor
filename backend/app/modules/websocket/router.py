"""
WebSocket routes for real-time updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .service import manager
from loguru import logger
import uuid

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    
    URL: ws://localhost:8000/api/v1/ws
    
    Events broadcasted:
    - violation_created: New violation detected
    - violation_resolved: Violation marked as resolved
    - violation_deleted: Violation deleted
    - agent_status_changed: Agent online/offline status changed
    - agent_updated: Agent details updated
    - agent_deleted: Agent deleted
    - rule_updated: Rule details updated
    - rule_toggled: Rule active status toggled
    - rule_deleted: Rule deleted
    """
    client_id = str(uuid.uuid4())
    
    try:
        await manager.connect(websocket, client_id)
        
        # Send welcome message
        await manager.send_personal_message({
            "event": "connected",
            "data": {
                "client_id": client_id,
                "message": "Connected to Baseline Monitor WebSocket"
            }
        }, client_id)
        
        # Keep connection alive and listen for client messages
        while True:
            # Wait for any message from client (heartbeat/ping)
            data = await websocket.receive_json()
            
            # Handle ping/pong for keepalive
            if data.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong"
                }, client_id)
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected normally")
    
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)
