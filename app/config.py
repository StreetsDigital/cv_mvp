from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os

class Settings(BaseSettings):
    # Required API Keys
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    
    # Application Settings
    app_name: str = Field("CV Automation MVP", env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    cors_origins: List[str] = Field(
        default=["https://recruitment.automateengage.com", "http://localhost:3000"]
    )
    
    # Enhanced CV Processing Settings
    enable_enhanced_processing: bool = Field(True, env="ENABLE_ENHANCED_PROCESSING")
    enhanced_processing_timeout: int = Field(60, env="ENHANCED_PROCESSING_TIMEOUT")  # seconds
    claude_model: str = Field("claude-3-sonnet-20240229", env="CLAUDE_MODEL")
    max_cv_length: int = Field(50000, env="MAX_CV_LENGTH")  # characters
    max_job_description_length: int = Field(10000, env="MAX_JOB_DESCRIPTION_LENGTH")  # characters
    
    # Enhanced Scoring Weights (can be overridden via environment)
    platform_expertise_weight: float = Field(0.20, env="PLATFORM_EXPERTISE_WEIGHT")
    campaign_performance_weight: float = Field(0.15, env="CAMPAIGN_PERFORMANCE_WEIGHT")
    creative_skills_weight: float = Field(0.12, env="CREATIVE_SKILLS_WEIGHT")
    analytics_skills_weight: float = Field(0.13, env="ANALYTICS_SKILLS_WEIGHT")
    seo_sem_weight: float = Field(0.08, env="SEO_SEM_WEIGHT")
    martech_operations_weight: float = Field(0.08, env="MARTECH_OPERATIONS_WEIGHT")
    advanced_analytics_weight: float = Field(0.07, env="ADVANCED_ANALYTICS_WEIGHT")
    industry_specialization_weight: float = Field(0.05, env="INDUSTRY_SPECIALIZATION_WEIGHT")
    platform_leadership_weight: float = Field(0.04, env="PLATFORM_LEADERSHIP_WEIGHT")
    sales_marketing_integration_weight: float = Field(0.03, env="SALES_MARKETING_INTEGRATION_WEIGHT")
    remote_work_capability_weight: float = Field(0.03, env="REMOTE_WORK_CAPABILITY_WEIGHT")
    executive_presence_weight: float = Field(0.02, env="EXECUTIVE_PRESENCE_WEIGHT")
    
    # Performance Settings
    enable_skill_caching: bool = Field(True, env="ENABLE_SKILL_CACHING")
    cache_expiry_hours: int = Field(24, env="CACHE_EXPIRY_HOURS")
    
    # Security
    secret_key: str = Field("mvp-secret-key-change-in-production", env="SECRET_KEY")
    
    # Chat Settings
    max_message_length: int = Field(4000, env="MAX_MESSAGE_LENGTH")
    max_file_size_mb: int = Field(5, env="MAX_FILE_SIZE_MB")
    allowed_file_types: List[str] = Field(
        default=["pdf", "docx", "txt"]
    )
    
    # Feature Flags (MVP Limitations)
    enable_vector_storage: bool = Field(False, env="ENABLE_VECTOR_STORAGE")
    enable_email_integration: bool = Field(False, env="ENABLE_EMAIL_INTEGRATION")
    enable_linkedin_integration: bool = Field(False, env="ENABLE_LINKEDIN_INTEGRATION")
    enable_analytics: bool = Field(False, env="ENABLE_ANALYTICS")
    enable_workflow_persistence: bool = Field(False, env="ENABLE_WORKFLOW_PERSISTENCE")
    
    # Premium Contact
    premium_contact_email: str = Field("andrew@automateengage.com", env="PREMIUM_CONTACT_EMAIL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()