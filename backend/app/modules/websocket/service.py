"""
WebSocket Manager for real-time updates
Handles client connections and broadcasts events
"""

from typing import Dict, List
from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self):
        # Active connections: {client_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and register a new client connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket client connected: {client_id}. Total: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str):
        """Remove a client from active connections"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket client disconnected: {client_id}. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict, exclude: List[str] = None):
        """Broadcast message to all connected clients (optionally exclude some)"""
        exclude = exclude or []
        disconnected = []
        
        for client_id, connection in self.active_connections.items():
            if client_id not in exclude:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def broadcast_violation_created(self, violation_data: dict):
        """Broadcast when a new violation is created"""
        await self.broadcast({
            "event": "violation_created",
            "data": violation_data
        })
        logger.info(f"Broadcasted violation_created: {violation_data.get('id')}")
    
    async def broadcast_violation_resolved(self, violation_data: dict):
        """Broadcast when a violation is resolved"""
        await self.broadcast({
            "event": "violation_resolved",
            "data": violation_data
        })
        logger.info(f"Broadcasted violation_resolved: {violation_data.get('id')}")
    
    async def broadcast_violation_deleted(self, violation_id: str):
        """Broadcast when a violation is deleted"""
        await self.broadcast({
            "event": "violation_deleted",
            "data": {"id": violation_id}
        })
        logger.info(f"Broadcasted violation_deleted: {violation_id}")
    
    async def broadcast_agent_status_changed(self, agent_data: dict):
        """Broadcast when agent status changes (online/offline)"""
        await self.broadcast({
            "event": "agent_status_changed",
            "data": agent_data
        })
        logger.info(f"Broadcasted agent_status_changed: {agent_data.get('id')}")
    
    async def broadcast_agent_updated(self, agent_data: dict):
        """Broadcast when agent details are updated"""
        await self.broadcast({
            "event": "agent_updated",
            "data": agent_data
        })
        logger.info(f"Broadcasted agent_updated: {agent_data.get('id')}")
    
    async def broadcast_agent_deleted(self, agent_id: str):
        """Broadcast when an agent is deleted"""
        await self.broadcast({
            "event": "agent_deleted",
            "data": {"id": agent_id}
        })
        logger.info(f"Broadcasted agent_deleted: {agent_id}")
    
    async def broadcast_rule_updated(self, rule_data: dict):
        """Broadcast when a rule is updated"""
        await self.broadcast({
            "event": "rule_updated",
            "data": rule_data
        })
        logger.info(f"Broadcasted rule_updated: {rule_data.get('id')}")
    
    async def broadcast_rule_toggled(self, rule_data: dict):
        """Broadcast when a rule is toggled (active/inactive)"""
        await self.broadcast({
            "event": "rule_toggled",
            "data": rule_data
        })
        logger.info(f"Broadcasted rule_toggled: {rule_data.get('id')}")
    
    async def broadcast_rule_deleted(self, rule_id: str):
        """Broadcast when a rule is deleted"""
        await self.broadcast({
            "event": "rule_deleted",
            "data": {"id": rule_id}
        })
        logger.info(f"Broadcasted rule_deleted: {rule_id}")


# Global instance
manager = ConnectionManager()
