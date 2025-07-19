from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SeniorityLevel(str, Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    DIRECTOR = "director"
    VP = "vp"
    EXECUTIVE = "executive"

class CompanyType(str, Enum):
    STARTUP = "startup"
    SCALE_UP = "scale_up"
    ENTERPRISE = "enterprise"
    CONSULTING = "consulting"
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"
    FREELANCE = "freelance"

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class WorkStyle(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on_site"
    FLEXIBLE = "flexible"

class ContactInfo(BaseModel):
    """Enhanced contact information with validation"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    linkedin: Optional[str] = Field(None, pattern=r'^https?://.*linkedin\.com/.*')
    location: Optional[str] = None
    github: Optional[str] = Field(None, pattern=r'^https?://.*github\.com/.*')
    portfolio: Optional[str] = Field(None, pattern=r'^https?://.*')
    timezone: Optional[str] = None
    work_authorization: Optional[str] = None
    relocation_willingness: Optional[bool] = None

class Certification(BaseModel):
    """Professional certification"""
    name: str = Field(..., min_length=1, max_length=200)
    issuer: str = Field(..., min_length=1, max_length=200)
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    credential_id: Optional[str] = None

class Education(BaseModel):
    """Enhanced education entry with validation"""
    degree: str = Field(..., min_length=1, max_length=200)
    institution: str = Field(..., min_length=1, max_length=200)
    graduation_year: Optional[int] = Field(None, ge=1950, le=2030)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    field_of_study: Optional[str] = None
    institution_ranking: Optional[int] = Field(None, ge=1, le=1000)
    honors: Optional[str] = None
    relevant_coursework: List[str] = Field(default_factory=list)

class Achievement(BaseModel):
    """Professional achievement or accomplishment"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=500)
    quantifiable_result: Optional[str] = None
    date: Optional[datetime] = None

class Experience(BaseModel):
    """Enhanced work experience with comprehensive tracking"""
    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    duration_months: int = Field(..., ge=0, le=600)
    description: Optional[str] = Field(None, max_length=2000)
    skills_used: List[str] = Field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    company_type: Optional[CompanyType] = None
    seniority_level: Optional[SeniorityLevel] = None
    team_size: Optional[int] = Field(None, ge=0, le=10000)
    direct_reports: Optional[int] = Field(None, ge=0, le=1000)
    achievements: List[Achievement] = Field(default_factory=list)
    technologies_used: List[str] = Field(default_factory=list)
    is_leadership_role: bool = False
    is_remote: bool = False
    
    @validator('skills_used', 'technologies_used')
    def validate_skills(cls, v):
        return [skill.strip().lower() for skill in v if skill.strip()]

class SkillAssessment(BaseModel):
    """Detailed skill assessment"""
    skill_name: str
    proficiency_level: SkillLevel
    years_experience: Optional[float] = None
    last_used: Optional[datetime] = None
    certified: bool = False

class DigitalPresence(BaseModel):
    """Digital presence and portfolio"""
    linkedin_profile_quality: Optional[int] = Field(None, ge=1, le=10)
    github_activity_score: Optional[int] = Field(None, ge=0, le=100)
    portfolio_quality: Optional[int] = Field(None, ge=1, le=10)
    professional_references: List[str] = Field(default_factory=list)
    publications: List[str] = Field(default_factory=list)
    speaking_engagements: List[str] = Field(default_factory=list)
    awards: List[str] = Field(default_factory=list)

class CompensationExpectations(BaseModel):
    """Compensation and logistics"""
    salary_expectation_min: Optional[int] = None
    salary_expectation_max: Optional[int] = None
    current_salary: Optional[int] = None
    benefits_requirements: List[str] = Field(default_factory=list)
    start_date_availability: Optional[datetime] = None
    notice_period_days: Optional[int] = Field(None, ge=0, le=365)
    travel_availability: Optional[int] = Field(None, ge=0, le=100)  # Percentage

class CandidateCV(BaseModel):
    """Comprehensive CV data model following the complete framework"""
    
    # Core Information
    name: str = Field(..., min_length=1, max_length=100)
    contact: ContactInfo
    professional_summary: Optional[str] = Field(None, max_length=1000)
    
    # Experience Analysis
    experience: List[Experience] = Field(default_factory=list)
    total_experience_years: float = Field(0.0, ge=0.0, le=50.0)
    relevant_experience_years: Optional[float] = None
    current_seniority_level: Optional[SeniorityLevel] = None
    employment_gaps_months: Optional[int] = Field(None, ge=0, le=600)
    average_tenure_months: Optional[float] = None
    industry_experience: List[str] = Field(default_factory=list)
    
    # Skills Assessment
    skills: List[str] = Field(default_factory=list)  # Simple list for backward compatibility
    detailed_skills: List[SkillAssessment] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    emerging_tech_familiarity: List[str] = Field(default_factory=list)
    
    # Education & Qualifications
    education: List[Education] = Field(default_factory=list)
    highest_degree: Optional[str] = None
    graduation_year: Optional[int] = None
    continuing_education: List[str] = Field(default_factory=list)
    
    # Performance Indicators
    achievements: List[Achievement] = Field(default_factory=list)
    digital_presence: Optional[DigitalPresence] = None
    
    # Cultural & Soft Skills
    communication_skills_score: Optional[int] = Field(None, ge=1, le=10)
    leadership_experience_years: Optional[float] = None
    cross_functional_experience: bool = False
    preferred_work_style: Optional[WorkStyle] = None
    adaptability_score: Optional[int] = Field(None, ge=1, le=10)
    
    # Compensation & Logistics
    compensation_expectations: Optional[CompensationExpectations] = None
    
    # Risk Assessment
    background_check_required: bool = False
    potential_red_flags: List[str] = Field(default_factory=list)
    cultural_fit_indicators: List[str] = Field(default_factory=list)
    retention_probability_score: Optional[int] = Field(None, ge=1, le=10)
    
    @validator('skills', pre=True)
    def normalize_skills(cls, v):
        if isinstance(v, str):
            return [skill.strip().lower() for skill in v.split(',') if skill.strip()]
        return [skill.strip().lower() for skill in v if skill.strip()]
    
    @validator('total_experience_years')
    def calculate_experience(cls, v, values):
        if 'experience' in values and values['experience']:
            calculated = sum(exp.duration_months for exp in values['experience']) / 12
            return round(calculated, 1)
        return v
    
    @validator('average_tenure_months')
    def calculate_average_tenure(cls, v, values):
        if 'experience' in values and values['experience'] and len(values['experience']) > 0:
            total_months = sum(exp.duration_months for exp in values['experience'])
            return round(total_months / len(values['experience']), 1)
        return v

class JobRequirements(BaseModel):
    """Enhanced job requirements with comprehensive criteria"""
    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    
    # Skills Requirements
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    emerging_tech_requirements: List[str] = Field(default_factory=list)
    
    # Experience Requirements
    min_experience_years: float = Field(0.0, ge=0.0, le=50.0)
    max_experience_years: Optional[float] = Field(None, ge=0.0, le=50.0)
    required_seniority_level: Optional[SeniorityLevel] = None
    leadership_required: bool = False
    industry_experience_required: List[str] = Field(default_factory=list)
    
    # Education Requirements
    education_requirements: List[str] = Field(default_factory=list)
    certification_requirements: List[str] = Field(default_factory=list)
    degree_required: bool = False
    
    # Location & Work Style
    location_requirements: Optional[str] = None
    work_style: Optional[WorkStyle] = None
    travel_requirement_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    # Compensation
    salary_range_min: Optional[int] = None
    salary_range_max: Optional[int] = None
    
    @validator('required_skills', 'preferred_skills', 'emerging_tech_requirements')
    def normalize_skills(cls, v):
        return [skill.strip().lower() for skill in v if skill.strip()]

class ComprehensiveScore(BaseModel):
    """Comprehensive scoring breakdown following the framework"""
    
    # Overall Scores
    overall_match_score: float = Field(0.0, ge=0.0, le=100.0)
    confidence_score: int = Field(1, ge=1, le=10)
    
    # Core Scoring Categories
    skills_match_score: float = Field(0.0, ge=0.0, le=100.0)
    experience_relevance_score: float = Field(0.0, ge=0.0, le=100.0)
    cultural_fit_score: float = Field(0.0, ge=0.0, le=100.0)
    growth_potential_score: float = Field(0.0, ge=0.0, le=100.0)
    
    # Detailed Breakdowns
    technical_skills_score: float = Field(0.0, ge=0.0, le=100.0)
    soft_skills_score: float = Field(0.0, ge=0.0, le=100.0)
    leadership_score: float = Field(0.0, ge=0.0, le=100.0)
    education_score: float = Field(0.0, ge=0.0, le=100.0)
    career_progression_score: float = Field(0.0, ge=0.0, le=100.0)
    
    # Risk Assessment
    job_stability_score: float = Field(0.0, ge=0.0, le=100.0)
    retention_probability: float = Field(0.0, ge=0.0, le=100.0)
    
    # Detailed Analysis
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommendation: str = ""
    suggested_interview_questions: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    salary_recommendation: Optional[str] = None