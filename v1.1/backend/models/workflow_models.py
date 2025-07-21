from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .cv_models import CandidateCV, JobRequirements, MatchScore

class ActionType(str, Enum):
    LINKEDIN_SEARCH = "linkedin_search"
    EMAIL_FOLLOW_UP = "email_follow_up"

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    HUMAN_REVIEW = "human_review"
    ACTION_SELECTION = "action_selection"
    CONTENT_GENERATION = "content_generation"
    FINAL_APPROVAL = "final_approval"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"

class ProcessStep(BaseModel):
    """Individual process step with explanation"""
    step_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    human_intervention_available: bool = Field(False)
    status: str = Field("completed")  # completed, pending, failed

class WorkflowState(BaseModel):
    """Enhanced workflow state with process explanation"""
    id: str = Field(..., min_length=1)
    cv_data: CandidateCV
    job_requirements: JobRequirements
    match_score: MatchScore
    status: WorkflowStatus = WorkflowStatus.PENDING
    selected_action: Optional[ActionType] = None
    linkedin_profiles: List[Dict[str, Any]] = Field(default_factory=list)
    email_content: Optional[str] = Field(None, max_length=5000)
    email_subject: Optional[str] = Field(None, max_length=200)
    human_feedback: Optional[str] = Field(None, max_length=1000)
    final_outcome: Optional[str] = Field(None, regex=r'^(approved|rejected|pending)$')
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Enhanced process tracking
    process_steps: List[ProcessStep] = Field(default_factory=list)
    current_step: int = Field(0)
    explanation_log: List[Dict[str, Any]] = Field(default_factory=list)
    human_interventions: List[Dict[str, Any]] = Field(default_factory=list)
    
    def update_status(self, new_status: WorkflowStatus):
        """Update status with timestamp"""
        self.status = new_status
        self.updated_at = datetime.now()
    
    def add_process_step(self, step: ProcessStep):
        """Add a new process step"""
        self.process_steps.append(step)
        self.current_step = step.step_number
        self.updated_at = datetime.now()

class EmailTemplate(BaseModel):
    """Email template with validation"""
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=5000)
    recipient_email: EmailStr
    sender_name: str = Field("Recruiting Team", max_length=100)
    
    class Config:
        schema_extra = {
            "example": {
                "subject": "Exciting Opportunity at TechCorp",
                "body": "Dear John,\n\nI hope this email finds you well...",
                "recipient_email": "candidate@example.com",
                "sender_name": "Sarah from HR"
            }
        }
