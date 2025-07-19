import logging
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional

# Local imports
from .config import settings
from .models.api_models import (
    ChatMessage, ChatResponse, CVAnalysisRequest, CVAnalysisResponse,
    FileUploadResponse, ActionTrackingRequest, ActionTrackingResponse
)
from .services.chat_service import ChatService
from .services.cv_processor import CVProcessor
from .middleware.rate_limiting import check_rate_limit
from .middleware.action_tracking import action_tracker
from .utils.file_utils import FileProcessor

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="CV Automation and Analysis API",
    version="1.0.0",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize services
chat_service = ChatService()
cv_processor = CVProcessor()
file_processor = FileProcessor()

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page"""
    try:
        with open("frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>CV Automation</title></head>
        <body>
            <h1>CV Automation API</h1>
            <p>Frontend not found. API is running at <a href="/docs">/docs</a></p>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: ChatMessage,
    request: Request,
    session_id: Optional[str] = None
):
    """Chat endpoint for conversational CV analysis"""
    
    # Check rate limits
    rate_limit_response = check_rate_limit(request)
    if rate_limit_response:
        raise HTTPException(status_code=429, detail=rate_limit_response)
    
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    try:
        # Track action for modal system
        action_data = action_tracker.track_action(session_id)
        
        # Process chat message
        response = await chat_service.process_message(message, session_id)
        
        # Add action tracking data to response
        if action_data.get("show_modal"):
            response.metadata.update(action_data)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...)
):
    """File upload endpoint for CV analysis"""
    
    # Check rate limits
    rate_limit_response = check_rate_limit(request)
    if rate_limit_response:
        raise HTTPException(status_code=429, detail=rate_limit_response)
    
    try:
        # Validate file type
        if not file_processor.validate_file_type(file.filename, settings.allowed_file_types):
            return FileUploadResponse(
                success=False,
                message=f"File type not supported. Allowed types: {', '.join(settings.allowed_file_types)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        if not file_processor.validate_file_size(file_content, settings.max_file_size_mb):
            return FileUploadResponse(
                success=False,
                message=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )
        
        # Extract text from file
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        extracted_text = file_processor.extract_text_from_file(file_content, file_extension)
        
        if not extracted_text:
            return FileUploadResponse(
                success=False,
                message="Could not extract text from file"
            )
        
        # Generate file ID for reference
        file_id = str(uuid.uuid4())
        
        return FileUploadResponse(
            success=True,
            message="File uploaded and processed successfully",
            file_id=file_id,
            file_content=extracted_text
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return FileUploadResponse(
            success=False,
            message="Error processing file"
        )

@app.post("/api/analyze", response_model=CVAnalysisResponse)
async def analyze_cv(
    request: Request,
    analysis_request: CVAnalysisRequest
):
    """Direct CV analysis endpoint"""
    
    # Check rate limits
    rate_limit_response = check_rate_limit(request)
    if rate_limit_response:
        raise HTTPException(status_code=429, detail=rate_limit_response)
    
    try:
        # Extract CV data
        cv_data = cv_processor.extract_cv_data(analysis_request.cv_text)
        
        # Parse job requirements (simplified)
        from .services.chat_service import ChatService
        chat_service_instance = ChatService()
        job_requirements = chat_service_instance._parse_job_description(analysis_request.job_description)
        
        # Perform analysis
        analysis_result = cv_processor.analyze_cv_match(cv_data, job_requirements)
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error analyzing CV: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing CV")

@app.post("/api/track-action", response_model=ActionTrackingResponse)
async def track_action(
    tracking_request: ActionTrackingRequest
):
    """Track user actions for modal system"""
    
    try:
        action_data = action_tracker.track_action(tracking_request.session_id)
        
        return ActionTrackingResponse(
            show_modal=action_data["show_modal"],
            action_count=action_data["action_count"],
            next_modal_at=action_data.get("next_modal_at"),
            modal_data=action_data.get("modal_data")
        )
        
    except Exception as e:
        logger.error(f"Error tracking action: {str(e)}")
        raise HTTPException(status_code=500, detail="Error tracking action")

@app.get("/api/limitations/{feature}")
async def get_feature_limitation(feature: str):
    """Get limitation information for a premium feature"""
    
    from .services.mvp_limitations import MVPLimitationHandler
    limitation_handler = MVPLimitationHandler()
    
    if not limitation_handler.is_feature_enabled(feature):
        limitation_data = limitation_handler.get_limitation_message(feature)
        return JSONResponse(content=limitation_data)
    
    return {"enabled": True}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "message": "The requested resource was not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "An unexpected error occurred"}
    )

# Additional endpoints for frontend integration
@app.get("/api/config")
async def get_app_config():
    """Get application configuration for frontend"""
    return {
        "app_name": settings.app_name,
        "max_file_size_mb": settings.max_file_size_mb,
        "allowed_file_types": settings.allowed_file_types,
        "max_message_length": settings.max_message_length,
        "premium_contact_email": settings.premium_contact_email,
        "features": {
            "email_integration": settings.enable_email_integration,
            "linkedin_integration": settings.enable_linkedin_integration,
            "analytics": settings.enable_analytics,
            "vector_storage": settings.enable_vector_storage,
            "workflow_persistence": settings.enable_workflow_persistence
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )