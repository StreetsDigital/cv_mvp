"""
WebSocket service for real-time process explanation
Handles real-time communication between backend analysis and frontend UI
"""

import logging
import json
import asyncio
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

from ..explainers.process_explainer import ProcessExplainer
from ...integration.claude_code.claude_code_integration import ClaudeCodeCVProcessor

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time process updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, Set[str]] = {}  # session_id -> set of connection_ids
        self.cv_processor: Optional[ClaudeCodeCVProcessor] = None
    
    def set_cv_processor(self, processor: ClaudeCodeCVProcessor):
        """Set the CV processor for handling analysis requests"""
        self.cv_processor = processor
    
    async def connect(self, websocket: WebSocket, session_id: str, connection_id: str = None):
        """Accept WebSocket connection and register it"""
        await websocket.accept()
        
        if not connection_id:
            connection_id = f"conn_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.active_connections[connection_id] = websocket
        
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(connection_id)
        
        logger.info(f"WebSocket connected: {connection_id} for session {session_id}")
        
        # Send connection confirmation
        await self.send_to_connection(connection_id, {
            "type": "connection_established",
            "connection_id": connection_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return connection_id
    
    def disconnect(self, connection_id: str, session_id: str = None):
        """Disconnect and clean up WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from session connections
        if session_id and session_id in self.session_connections:
            self.session_connections[session_id].discard(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        """Broadcast message to all connections in a session"""
        if session_id in self.session_connections:
            disconnected_connections = []
            for connection_id in self.session_connections[session_id]:
                try:
                    await self.send_to_connection(connection_id, message)
                except Exception as e:
                    logger.error(f"Failed to broadcast to {connection_id}: {e}")
                    disconnected_connections.append(connection_id)
            
            # Clean up failed connections
            for conn_id in disconnected_connections:
                self.disconnect(conn_id, session_id)
    
    async def handle_analysis_request(self, session_id: str, request_data: Dict[str, Any]):
        """Handle CV analysis request with real-time updates"""
        if not self.cv_processor:
            raise ValueError("CV processor not initialized")
        
        try:
            # Create WebSocket callback for real-time updates
            async def websocket_callback(message: Dict[str, Any]):
                await self.broadcast_to_session(session_id, message)
            
            # Start analysis with real-time explanation
            result = await self.cv_processor.analyze_cv_with_explanation(
                cv_text=request_data.get("cv_text"),
                job_description=request_data.get("job_description"),
                session_id=session_id,
                detail_level=request_data.get("detail_level", "moderate"),
                websocket_callback=websocket_callback
            )
            
            # Send final result
            await self.broadcast_to_session(session_id, {
                "type": "analysis_complete",
                "session_id": session_id,
                "result": {
                    "overall_score": result["match_score"].overall_score,
                    "candidate_name": result["cv_data"].name,
                    "job_title": result["job_requirements"].title,
                    "recommendations": result["recommendations"],
                    "process_summary": result["process_summary"]
                },
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed for session {session_id}: {e}")
            await self.broadcast_to_session(session_id, {
                "type": "analysis_error",
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    async def handle_human_intervention(
        self, 
        session_id: str, 
        intervention_data: Dict[str, Any]
    ):
        """Handle human intervention response"""
        if not self.cv_processor:
            raise ValueError("CV processor not initialized")
        
        try:
            result = await self.cv_processor.handle_human_intervention(
                session_id=session_id,
                intervention_type=intervention_data.get("intervention_type"),
                decision=intervention_data.get("decision"),
                data=intervention_data.get("data", {})
            )
            
            # Broadcast intervention result
            await self.broadcast_to_session(session_id, {
                "type": "intervention_processed",
                "session_id": session_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Intervention handling failed for session {session_id}: {e}")
            await self.broadcast_to_session(session_id, {
                "type": "intervention_error",
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status information for a session"""
        return {
            "session_id": session_id,
            "active_connections": len(self.session_connections.get(session_id, set())),
            "connection_ids": list(self.session_connections.get(session_id, set())),
            "cv_processor_status": "available" if self.cv_processor else "not_available"
        }
    
    def get_all_sessions(self) -> Dict[str, Any]:
        """Get status of all active sessions"""
        return {
            session_id: self.get_session_status(session_id)
            for session_id in self.session_connections.keys()
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

# WebSocket endpoint handler
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Main WebSocket endpoint for process explanation"""
    connection_id = None
    
    try:
        connection_id = await websocket_manager.connect(websocket, session_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "start_analysis":
                await websocket_manager.handle_analysis_request(session_id, message.get("data", {}))
            
            elif message_type == "human_intervention":
                await websocket_manager.handle_human_intervention(session_id, message.get("data", {}))
            
            elif message_type == "ping":
                await websocket_manager.send_to_connection(connection_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "get_session_status":
                status = websocket_manager.get_session_status(session_id)
                await websocket_manager.send_to_connection(connection_id, {
                    "type": "session_status",
                    "data": status
                })
            
            else:
                await websocket_manager.send_to_connection(connection_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if connection_id:
            websocket_manager.disconnect(connection_id, session_id)
