from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List

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
    """CV analysis response"""
    success: bool
    candidate_name: str
    overall_score: float
    recommendation: str
    analysis: Dict[str, Any]

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