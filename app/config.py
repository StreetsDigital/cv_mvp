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