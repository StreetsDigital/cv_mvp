"""
WebSocket Manager for Real-Time CV Analysis Updates
Handles connection lifecycle, message broadcasting, and session management
"""

import json
import logging
import asyncio
from typing import Dict, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
import uuid

logger = logging.getLogger(__name__)


class WebSocketMessage(BaseModel):
    """Standard message format for WebSocket communication"""
    type: str = Field(..., description="Message type (process_update, intervention_request, etc.)")
    session_id: str = Field(..., description="Analysis session ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProcessUpdate(BaseModel):
    """Process update message structure"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    step_name: str
    status: str = Field(..., regex="^(started|in_progress|completed|failed|intervention_required)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    details: Optional[Dict[str, Any]] = None
    requires_intervention: bool = False
    intervention_type: Optional[str] = None


class ConnectionInfo(BaseModel):
    """WebSocket connection information"""
    connection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_ping: datetime = Field(default_factory=datetime.utcnow)
    client_info: Dict[str, Any] = Field(default_factory=dict)


class WebSocketManager:
    """
    Manages WebSocket connections for real-time CV analysis updates
    """
    
    def __init__(self):
        # Connection pools organized by session_id
        self._connections: Dict[str, Set[WebSocket]] = {}
        # Connection metadata
        self._connection_info: Dict[WebSocket, ConnectionInfo] = {}
        # Active sessions
        self._active_sessions: Set[str] = set()
        # Message queue for reliability
        self._message_queue: Dict[str, list] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
        
    async def connect(self, websocket: WebSocket, session_id: str, client_info: Optional[Dict] = None) -> str:
        """
        Accept and register a new WebSocket connection
        
        Args:
            websocket: The WebSocket connection
            session_id: CV analysis session ID
            client_info: Optional client metadata
            
        Returns:
            connection_id: Unique connection identifier
        """
        await websocket.accept()
        
        async with self._lock:
            # Create connection info
            conn_info = ConnectionInfo(
                session_id=session_id,
                client_info=client_info or {}
            )
            
            # Add to connection pool
            if session_id not in self._connections:
                self._connections[session_id] = set()
                self._message_queue[session_id] = []
            
            self._connections[session_id].add(websocket)
            self._connection_info[websocket] = conn_info
            self._active_sessions.add(session_id)
            
            logger.info(f"WebSocket connected: session={session_id}, connection={conn_info.connection_id}")
            
            # Send connection confirmation
            await self._send_direct(websocket, {
                "type": "connection_established",
                "session_id": session_id,
                "connection_id": conn_info.connection_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Send any queued messages
            await self._send_queued_messages(websocket, session_id)
            
            return conn_info.connection_id
    
    async def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection
        
        Args:
            websocket: The WebSocket connection to remove
        """
        async with self._lock:
            if websocket in self._connection_info:
                conn_info = self._connection_info[websocket]
                session_id = conn_info.session_id
                
                # Remove from connection pool
                if session_id in self._connections:
                    self._connections[session_id].discard(websocket)
                    
                    # Clean up empty sessions
                    if not self._connections[session_id]:
                        del self._connections[session_id]
                        self._active_sessions.discard(session_id)
                        # Keep message queue for reconnection
                
                # Remove connection info
                del self._connection_info[websocket]
                
                logger.info(f"WebSocket disconnected: session={session_id}, connection={conn_info.connection_id}")
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        """
        Broadcast a message to all connections in a session
        
        Args:
            session_id: Target session ID
            message: Message to broadcast
        """
        async with self._lock:
            if session_id not in self._connections:
                # Queue message for future connections
                if session_id not in self._message_queue:
                    self._message_queue[session_id] = []
                self._message_queue[session_id].append(message)
                return
            
            # Send to all connections in parallel
            disconnected = []
            tasks = []
            
            for websocket in self._connections[session_id]:
                tasks.append(self._send_safe(websocket, message, disconnected))
            
            await asyncio.gather(*tasks)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                await self.disconnect(ws)
    
    async def send_process_update(self, session_id: str, update: ProcessUpdate):
        """
        Send a process update to all connections in a session
        
        Args:
            session_id: Target session ID
            update: Process update information
        """
        message = WebSocketMessage(
            type="process_update",
            session_id=session_id,
            data=update.dict()
        )
        
        await self.broadcast_to_session(session_id, message.dict())
    
    async def request_intervention(self, session_id: str, intervention_type: str, 
                                 context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Request human intervention for a decision
        
        Args:
            session_id: Target session ID
            intervention_type: Type of intervention needed
            context: Context information for the intervention
            
        Returns:
            Intervention response or None if timeout
        """
        intervention_id = str(uuid.uuid4())
        
        message = WebSocketMessage(
            type="intervention_request",
            session_id=session_id,
            data={
                "intervention_id": intervention_id,
                "intervention_type": intervention_type,
                "context": context,
                "timeout": 30  # 30 second timeout
            }
        )
        
        await self.broadcast_to_session(session_id, message.dict())
        
        # Wait for intervention response (simplified - in production use proper async event handling)
        # This would be handled by a separate endpoint that receives the intervention response
        return None  # Placeholder
    
    async def _send_direct(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message directly to a WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    async def _send_safe(self, websocket: WebSocket, message: Dict[str, Any], 
                        disconnected: list):
        """Send a message safely, tracking disconnections"""
        try:
            await websocket.send_json(message)
        except (WebSocketDisconnect, ConnectionError):
            disconnected.append(websocket)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            disconnected.append(websocket)
    
    async def _send_queued_messages(self, websocket: WebSocket, session_id: str):
        """Send any queued messages to a newly connected client"""
        if session_id in self._message_queue and self._message_queue[session_id]:
            for message in self._message_queue[session_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending queued message: {e}")
                    break
            
            # Clear queue after sending
            self._message_queue[session_id] = []
    
    async def handle_client_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Handle incoming messages from clients
        
        Args:
            websocket: Source WebSocket
            message: Received message
        """
        if websocket not in self._connection_info:
            logger.warning("Message from unknown connection")
            return
        
        conn_info = self._connection_info[websocket]
        message_type = message.get("type")
        
        if message_type == "ping":
            # Update last ping time
            conn_info.last_ping = datetime.utcnow()
            await self._send_direct(websocket, {"type": "pong"})
            
        elif message_type == "intervention_response":
            # Handle intervention response
            # This would trigger an event that the waiting intervention request can receive
            pass
            
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a session"""
        return {
            "session_id": session_id,
            "active": session_id in self._active_sessions,
            "connection_count": len(self._connections.get(session_id, [])),
            "queued_messages": len(self._message_queue.get(session_id, []))
        }
    
    def get_all_sessions(self) -> list[str]:
        """Get all active session IDs"""
        return list(self._active_sessions)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()