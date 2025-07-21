"""
Enhanced FastAPI application with real-time process visualization
Combines original CV automation with new transparency features
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
from typing import Dict, Any
import uuid

from .config import settings
from .models.api_models import (
    CVSubmissionRequest, 
    CVSubmissionResponse,
    WorkflowActionRequest,
    WorkflowActionResponse
)
from .services.websocket_service import websocket_endpoint, websocket_manager
from ..integration.claude_code.claude_code_integration import ClaudeCodeCVProcessor

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Enhanced CV screening with real-time process visualization and transparency",
    version="1.1.0",
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Claude Code CV processor
cv_processor = ClaudeCodeCVProcessor(settings.anthropic_api_key)
websocket_manager.set_cv_processor(cv_processor)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Enhanced CV Screening with Process Visualization API", 
        "status": "healthy",
        "version": "1.1.0",
        "features": [
            "real_time_explanation",
            "human_in_loop",
            "process_transparency",
            "claude_code_integration"
        ]
    }

@app.websocket("/ws/analysis/{session_id}")
async def websocket_analysis_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time process explanation"""
    await websocket_endpoint(websocket, session_id)

@app.post("/api/cv/submit-enhanced", response_model=CVSubmissionResponse)
async def submit_cv_enhanced(request: CVSubmissionRequest):
    """Submit CV for enhanced processing with real-time explanation"""
    try:
        # Generate unique session ID
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"Starting enhanced CV analysis for session: {session_id}")
        
        return CVSubmissionResponse(
            workflow_id=session_id,
            status="processing",
            message=f"Enhanced CV analysis started. Connect to WebSocket /ws/analysis/{session_id} for real-time updates"
        )
    
    except Exception as e:
        logger.error(f"Enhanced CV submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Enhanced CV processing failed")

@app.post("/api/analysis/start")
async def start_analysis(
    cv_text: str,
    job_description: str,
    detail_level: str = "moderate"
):
    """Start CV analysis without WebSocket (for testing)"""
    try:
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        result = await cv_processor.analyze_cv_with_explanation(
            cv_text=cv_text,
            job_description=job_description,
            session_id=session_id,
            detail_level=detail_level
        )
        
        return {
            "session_id": session_id,
            "status": "completed",
            "result": {
                "overall_score": result["match_score"].overall_score,
                "candidate_name": result["cv_data"].name,
                "job_title": result["job_requirements"].title,
                "process_steps": len(result["process_explanation"]),
                "recommendations": result["recommendations"]
            }
        }
    
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post("/api/intervention/handle")
async def handle_intervention(
    session_id: str,
    intervention_type: str,
    decision: str,
    data: Dict[str, Any] = None
):
    """Handle human intervention decision"""
    try:
        result = await cv_processor.handle_human_intervention(
            session_id=session_id,
            intervention_type=intervention_type,
            decision=decision,
            data=data or {}
        )
        
        return {
            "session_id": session_id,
            "status": "processed",
            "result": result
        }
    
    except Exception as e:
        logger.error(f"Intervention handling failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Intervention handling failed")

@app.get("/api/sessions/active")
async def get_active_sessions():
    """Get information about active analysis sessions"""
    try:
        sessions = websocket_manager.get_all_sessions()
        processor_sessions = cv_processor.get_active_sessions()
        
        return {
            "websocket_sessions": sessions,
            "processor_sessions": processor_sessions,
            "total_active": len(sessions)
        }
    
    except Exception as e:
        logger.error(f"Failed to get active sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get session information")

@app.get("/api/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get status of specific session"""
    try:
        websocket_status = websocket_manager.get_session_status(session_id)
        return {
            "session_id": session_id,
            "websocket_status": websocket_status,
            "timestamp": logger.info("Session status retrieved")
        }
    
    except Exception as e:
        logger.error(f"Failed to get session status: {str(e)}")
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/api/health/detailed")
async def detailed_health_check():
    """Detailed health check with component status"""
    try:
        return {
            "status": "healthy",
            "version": "1.1.0",
            "components": {
                "cv_processor": "available" if cv_processor else "unavailable",
                "websocket_manager": "available",
                "anthropic_api": "configured" if settings.anthropic_api_key else "not_configured",
                "pinecone": "configured" if settings.pinecone_api_key else "not_configured"
            },
            "features": {
                "real_time_explanation": settings.real_time_updates,
                "human_intervention": settings.human_intervention_enabled,
                "scoring_explanation": settings.scoring_explanation_enabled,
                "pattern_matching": settings.pattern_matching_enabled,
                "industry_analysis": settings.industry_analysis_enabled
            },
            "settings": {
                "detail_level": settings.explanation_detail_level,
                "keyword_threshold": settings.keyword_confidence_threshold,
                "debug_mode": settings.debug
            }
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": "Invalid input", "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": "An unexpected error occurred"}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Enhanced CV Screening API starting up...")
    logger.info(f"Features enabled: Real-time updates: {settings.real_time_updates}, Human intervention: {settings.human_intervention_enabled}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Enhanced CV Screening API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
