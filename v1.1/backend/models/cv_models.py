from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ContactInfo(BaseModel):
    """Contact information with validation"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, regex=r'^\+?[\d\s\-\(\)]+$')
    linkedin: Optional[str] = Field(None, regex=r'^https?://.*linkedin\.com/.*')
    location: Optional[str] = None

class Education(BaseModel):
    """Education entry with validation"""
    degree: str = Field(..., min_length=1, max_length=200)
    institution: str = Field(..., min_length=1, max_length=200)
    graduation_year: Optional[int] = Field(None, ge=1950, le=2030)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)

class Experience(BaseModel):
    """Work experience with skills extraction"""
    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    duration_months: int = Field(..., ge=0, le=600)  # Max 50 years
    description: Optional[str] = Field(None, max_length=2000)
    skills_used: List[str] = Field(default_factory=list)
    
    @validator('skills_used')
    def validate_skills(cls, v):
        return [skill.strip().lower() for skill in v if skill.strip()]

class CandidateCV(BaseModel):
    """Main CV data model with comprehensive validation"""
    name: str = Field(..., min_length=1, max_length=100)
    contact: ContactInfo
    skills: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    total_experience_years: float = Field(0.0, ge=0.0, le=50.0)
    summary: Optional[str] = Field(None, max_length=1000)
    
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

class JobRequirements(BaseModel):
    """Job requirements with validation"""
    title: str = Field(..., min_length=1, max_length=200)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    min_experience_years: float = Field(0.0, ge=0.0, le=50.0)
    education_requirements: List[str] = Field(default_factory=list)
    company: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    
    @validator('required_skills', 'preferred_skills')
    def normalize_skills(cls, v):
        return [skill.strip().lower() for skill in v if skill.strip()]

class MatchScore(BaseModel):
    """Detailed scoring breakdown with explanations"""
    overall_score: float = Field(..., ge=0.0, le=100.0)
    skills_match_score: float = Field(..., ge=0.0, le=100.0)
    experience_score: float = Field(..., ge=0.0, le=100.0)
    education_score: float = Field(..., ge=0.0, le=100.0)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    explanation: str = Field(..., min_length=1, max_length=500)
    detailed_reasoning: Optional[Dict[str, Any]] = Field(default_factory=dict)
    confidence_level: float = Field(0.0, ge=0.0, le=1.0)
    
    @validator('overall_score', 'skills_match_score', 'experience_score', 'education_score')
    def round_scores(cls, v):
        return round(v, 1)
