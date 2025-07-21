from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from .cv_models import ComprehensiveScore

class ChatMessage(BaseModel):
    """Chat message model"""
    content: str = Field(..., min_length=1, max_length=4000)
    message_type: str = Field("text", pattern=r'^(text|file|system)$')
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    timestamp: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    content: str
    message_type: str = Field(default="text")
    workflow_id: Optional[str] = None
    requires_action: bool = Field(default=False)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CVAnalysisRequest(BaseModel):
    """CV analysis request"""
    cv_text: str = Field(..., min_length=1, max_length=50000)
    job_description: str = Field(..., min_length=1, max_length=10000)

class CVAnalysisResponse(BaseModel):
    """Enhanced CV analysis response with comprehensive scoring"""
    success: bool = True
    candidate_name: str
    candidate_email: Optional[str] = None
    overall_score: float = Field(..., ge=0.0, le=100.0)
    skills_match: float = Field(..., ge=0.0, le=100.0)
    experience_match: float = Field(..., ge=0.0, le=100.0)
    
    # Enhanced scoring breakdown
    detailed_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Skills extraction
    extracted_skills: List[str] = Field(default_factory=list)
    enhanced_skills: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Recommendations and insights
    recommendations: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    
    # Interview suggestions
    suggested_interview_questions: List[str] = Field(default_factory=list)
    
    # Metadata
    processing_time_ms: Optional[float] = None
    confidence_score: Optional[float] = None
    overall_score: float
    recommendation: str
    analysis: Dict[str, Any]  # Keep for backward compatibility
    comprehensive_score: Optional[ComprehensiveScore] = None  # New detailed scoring

class FileUploadResponse(BaseModel):
    """File upload response"""
    success: bool
    message: str
    file_id: Optional[str] = None
    file_content: Optional[str] = None

class ActionTrackingRequest(BaseModel):
    """Action tracking request"""
    session_id: str

class ActionTrackingResponse(BaseModel):
    """Action tracking response"""
    show_modal: bool
    action_count: int
    next_modal_at: Optional[int] = None
    modal_data: Optional[Dict[str, Any]] = None