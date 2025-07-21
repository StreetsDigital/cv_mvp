"""
WebSocket endpoints for real-time CV analysis communication
"""

import logging
from fastapi import WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional
import json

from ..services.websocket_manager import websocket_manager
from ..middleware.auth import get_current_user_optional

logger = logging.getLogger(__name__)


async def websocket_analysis_endpoint(
    websocket: WebSocket,
    session_id: str = Query(..., description="CV analysis session ID"),
    token: Optional[str] = Query(None, description="Optional authentication token")
):
    """
    WebSocket endpoint for real-time CV analysis updates
    
    Path: /ws/analysis/{session_id}
    
    Message Types:
    - process_update: Real-time analysis step updates
    - intervention_request: Request for human intervention
    - intervention_response: Human intervention decision
    - connection_established: Confirmation of connection
    - error: Error messages
    """
    
    # Optional authentication
    user = None
    if token:
        # Validate token if provided
        # user = await get_current_user_optional(token)
        pass
    
    # Client info for tracking
    client_info = {
        "user_agent": websocket.headers.get("user-agent", "unknown"),
        "origin": websocket.headers.get("origin", "unknown"),
        "authenticated": user is not None
    }
    
    try:
        # Connect to WebSocket manager
        connection_id = await websocket_manager.connect(
            websocket=websocket,
            session_id=session_id,
            client_info=client_info
        )
        
        logger.info(f"WebSocket connection established: {connection_id}")
        
        # Handle incoming messages
        while True:
            try:
                # Receive message from client
                raw_message = await websocket.receive_text()
                
                try:
                    message = json.loads(raw_message)
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Invalid JSON format"
                    })
                    continue
                
                # Process client message
                await websocket_manager.handle_client_message(websocket, message)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {connection_id}")
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up connection
        await websocket_manager.disconnect(websocket)


async def websocket_monitor_endpoint(
    websocket: WebSocket,
    admin_token: str = Query(..., description="Admin authentication token")
):
    """
    WebSocket endpoint for monitoring all active sessions (admin only)
    
    Path: /ws/monitor
    
    Provides real-time updates on all active CV analysis sessions
    """
    
    # Validate admin token
    # if not validate_admin_token(admin_token):
    #     await websocket.close(code=1008, reason="Unauthorized")
    #     return
    
    await websocket.accept()
    
    try:
        # Send initial session list
        sessions = websocket_manager.get_all_sessions()
        await websocket.send_json({
            "type": "session_list",
            "sessions": [
                websocket_manager.get_session_info(session_id)
                for session_id in sessions
            ]
        })
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                # Wait for client messages or timeout for periodic updates
                message = await websocket.receive_text()
                
                if message == "refresh":
                    sessions = websocket_manager.get_all_sessions()
                    await websocket.send_json({
                        "type": "session_list",
                        "sessions": [
                            websocket_manager.get_session_info(session_id)
                            for session_id in sessions
                        ]
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Monitor WebSocket error: {e}")
                break
                
    except Exception as e:
        logger.error(f"Monitor endpoint error: {e}")
    finally:
        await websocket.close()