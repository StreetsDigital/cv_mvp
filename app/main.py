import logging
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional

# Conditional WebSocket import for serverless compatibility
try:
    from fastapi import WebSocket
    from .endpoints.websocket_endpoints import websocket_analysis_endpoint, websocket_monitor_endpoint
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    WebSocket = None
    websocket_analysis_endpoint = None
    websocket_monitor_endpoint = None

# Local imports
from .config import settings
from .models.api_models import (
    ChatMessage, ChatResponse, CVAnalysisRequest, CVAnalysisResponse,
    FileUploadResponse, ActionTrackingRequest, ActionTrackingResponse
)
from .services.chat_service import ChatService
from .services.cv_processor import CVProcessor
from .services.enhanced_cv_processor import EnhancedCVProcessor  # New enhanced processor

# Conditional v1.1 processor import
try:
    from .services.enhanced_cv_processor_v11 import EnhancedCVProcessorV11
    V11_AVAILABLE = True
except ImportError:
    V11_AVAILABLE = False
    EnhancedCVProcessorV11 = None

from .middleware.rate_limiting import check_rate_limit
from .middleware.action_tracking import action_tracker
from .utils.file_utils import FileProcessor

# Conditional keep-alive import for Render deployment
try:
    from .services.keep_alive import KeepAliveService
    KEEP_ALIVE_AVAILABLE = True
except ImportError:
    KEEP_ALIVE_AVAILABLE = False
    KeepAliveService = None

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
enhanced_cv_processor = EnhancedCVProcessor(api_key=settings.anthropic_api_key)  # New enhanced processor
file_processor = FileProcessor()

# Initialize keep-alive service for Render deployment
keep_alive_service = None
if KEEP_ALIVE_AVAILABLE and hasattr(settings, 'app_url') and settings.app_url:
    keep_alive_service = KeepAliveService(settings.app_url)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page"""
    try:
        with open("frontend/index_standalone.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Fallback to regular index.html
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
    """Standard CV analysis endpoint"""
    
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
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post("/api/analyze-enhanced", response_model=CVAnalysisResponse)
async def analyze_cv_enhanced(
    request: Request,
    analysis_request: CVAnalysisRequest
):
    """Enhanced CV analysis endpoint with new skill categories"""
    
    # Check rate limits
    rate_limit_response = check_rate_limit(request)
    if rate_limit_response:
        raise HTTPException(status_code=429, detail=rate_limit_response)
    
    try:
        # Parse job requirements first
        from .models.cv_models import JobRequirements
        from .services.chat_service import ChatService
        
        chat_service_instance = ChatService()
        job_requirements = chat_service_instance._parse_job_description(analysis_request.job_description)
        
        # Convert to enhanced job requirements if needed
        if not isinstance(job_requirements, JobRequirements):
            # Create JobRequirements object from chat service output
            job_requirements = JobRequirements(
                title=getattr(job_requirements, 'title', 'Unknown Role'),
                company=getattr(job_requirements, 'company', 'Unknown Company'),
                description=analysis_request.job_description,
                required_skills=getattr(job_requirements, 'required_skills', []),
                preferred_skills=getattr(job_requirements, 'preferred_skills', [])
            )
        
        # Process CV with enhanced processor
        cv_data, comprehensive_score = await enhanced_cv_processor.process_enhanced_cv(
            analysis_request.cv_text, 
            job_requirements
        )
        
        # Convert comprehensive score to CVAnalysisResponse format
        analysis_result = CVAnalysisResponse(
            overall_score=comprehensive_score.overall_match_score,
            skills_match=comprehensive_score.skills_match_score,
            experience_match=comprehensive_score.experience_relevance_score,
            detailed_analysis={
                "seo_sem_score": comprehensive_score.seo_sem_score,
                "martech_score": comprehensive_score.martech_operations_score,
                "advanced_analytics_score": comprehensive_score.advanced_analytics_score,
                "industry_specialization_score": comprehensive_score.industry_specialization_score,
                "platform_leadership_score": comprehensive_score.platform_leadership_score,
                "remote_capability_score": comprehensive_score.remote_capability_score,
                "executive_readiness_score": comprehensive_score.executive_readiness_score,
                "traditional_scores": {
                    "technical_skills": comprehensive_score.technical_skills_score,
                    "leadership": comprehensive_score.leadership_score,
                    "education": comprehensive_score.education_score,
                    "cultural_fit": comprehensive_score.cultural_fit_score
                }
            },
            recommendations=comprehensive_score.suggested_interview_questions or [],
            candidate_name=cv_data.name,
            candidate_email=cv_data.contact.email if cv_data.contact else None,
            extracted_skills=cv_data.skills,
            enhanced_skills={
                "seo_sem": cv_data.seo_sem_expertise,
                "martech": cv_data.martech_proficiency,
                "advanced_analytics": cv_data.advanced_analytics_skills,
                "affiliate_marketing": cv_data.affiliate_marketing_experience,
                "influencer_marketing": cv_data.influencer_marketing_experience,
                "platform_leadership": cv_data.platform_leadership_experience,
                "industry_expertise": cv_data.industry_vertical_expertise,
                "remote_skills": cv_data.remote_collaboration_skills,
                "executive_skills": cv_data.executive_capabilities,
                "sales_marketing": cv_data.sales_marketing_integration_skills
            }
        )
        
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
            "workflow_persistence": settings.enable_workflow_persistence,
            "real_time_updates": True,  # V1.1 feature
            "human_intervention": True  # V1.1 feature
        }
    }

# WebSocket endpoints for real-time updates (if available)
if WEBSOCKET_AVAILABLE:
    from fastapi import Query
    
    @app.websocket("/ws/analysis")
    async def websocket_analysis(websocket: WebSocket, session_id: str = Query(...)):
        """WebSocket endpoint for real-time CV analysis updates"""
        await websocket_analysis_endpoint(websocket, session_id)

    @app.websocket("/ws/monitor")
    async def websocket_monitor(websocket: WebSocket, admin_token: str = Query(...)):
        """WebSocket endpoint for monitoring all sessions (admin only)"""
        await websocket_monitor_endpoint(websocket, admin_token)
else:
    logger.warning("WebSocket functionality not available in this deployment")

# Real-time analysis endpoint (if v1.1 features available)
if V11_AVAILABLE:
    from fastapi import Query
    
    @app.post("/api/analyze-realtime", response_model=CVAnalysisResponse)
    async def analyze_cv_realtime(
        request: Request,
        analysis_request: CVAnalysisRequest,
        session_id: str = Query(..., description="WebSocket session ID for real-time updates")
    ):
        """Real-time CV analysis endpoint with WebSocket updates"""
        
        # Check rate limits
        rate_limit_response = check_rate_limit(request)
        if rate_limit_response:
            raise HTTPException(status_code=429, detail=rate_limit_response)
        
        try:
            # Parse job requirements
            from .models.cv_models import JobRequirements
            from .services.chat_service import ChatService
            
            chat_service_instance = ChatService()
            job_requirements = chat_service_instance._parse_job_description(analysis_request.job_description)
            
            # Convert to enhanced job requirements if needed
            if not isinstance(job_requirements, JobRequirements):
                job_requirements = JobRequirements(
                    title=getattr(job_requirements, 'title', 'Unknown Role'),
                    company=getattr(job_requirements, 'company', 'Unknown Company'),
                    description=analysis_request.job_description,
                    required_skills=getattr(job_requirements, 'required_skills', []),
                    preferred_skills=getattr(job_requirements, 'preferred_skills', [])
                )
            
            # Initialize V1.1 processor with session ID
            enhanced_processor_v11 = EnhancedCVProcessorV11(
                api_key=settings.anthropic_api_key
            )
            
            # Process CV with real-time updates
            cv_data, comprehensive_score = await enhanced_processor_v11.process_enhanced_cv_with_updates(
                cv_text=analysis_request.cv_text,
                job_requirements=job_requirements,
                session_id=session_id
            )
            
            # Convert to API response format
            analysis_result = CVAnalysisResponse(
                overall_score=comprehensive_score.overall_match_score,
                skills_match=comprehensive_score.skills_match_score,
                experience_match=comprehensive_score.experience_relevance_score,
                detailed_analysis={
                    "seo_sem_score": comprehensive_score.seo_sem_score,
                    "martech_score": comprehensive_score.martech_operations_score,
                    "advanced_analytics_score": comprehensive_score.advanced_analytics_score,
                "industry_specialization_score": comprehensive_score.industry_specialization_score,
                "platform_leadership_score": comprehensive_score.platform_leadership_score,
                "remote_capability_score": comprehensive_score.remote_capability_score,
                "executive_readiness_score": comprehensive_score.executive_readiness_score,
                "traditional_scores": {
                    "technical_skills": comprehensive_score.technical_skills_score,
                    "leadership": comprehensive_score.leadership_score,
                    "education": comprehensive_score.education_score,
                    "cultural_fit": comprehensive_score.cultural_fit_score
                }
            },
            recommendations=comprehensive_score.suggested_interview_questions or [],
            candidate_name=cv_data.name,
            candidate_email=cv_data.contact.email if cv_data.contact else None,
            extracted_skills=cv_data.skills,
            enhanced_skills={
                "seo_sem": cv_data.seo_sem_expertise,
                "martech": cv_data.martech_proficiency,
                "advanced_analytics": cv_data.advanced_analytics_skills,
                "affiliate_marketing": cv_data.affiliate_marketing_experience,
                "influencer_marketing": cv_data.influencer_marketing_experience,
                "platform_leadership": cv_data.platform_leadership_experience,
                "industry_expertise": cv_data.industry_vertical_expertise,
                "remote_skills": cv_data.remote_collaboration_skills,
                "executive_skills": cv_data.executive_capabilities,
                "sales_marketing": cv_data.sales_marketing_integration_skills
            }
        )
        
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in real-time CV analysis: {str(e)}")
            raise HTTPException(status_code=500, detail="Error analyzing CV")

else:
    logger.warning("Real-time analysis features not available in this deployment")

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"Starting {settings.app_name}")
    
    # Start keep-alive service if available
    if keep_alive_service:
        import asyncio
        asyncio.create_task(keep_alive_service.start_keep_alive())
        logger.info("Keep-alive service started")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down application")
    
    # Stop keep-alive service
    if keep_alive_service:
        keep_alive_service.stop()
        logger.info("Keep-alive service stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )