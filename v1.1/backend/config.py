from pydantic import BaseSettings, Field
from typing import Optional
import os

class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    slack_bot_token: str = Field(..., env="SLACK_BOT_TOKEN")
    slack_signing_secret: str = Field(..., env="SLACK_SIGNING_SECRET")
    slack_app_token: str = Field(..., env="SLACK_APP_TOKEN")
    pinecone_api_key: str = Field(..., env="PINECONE_API_KEY")
    sendgrid_api_key: str = Field(..., env="SENDGRID_API_KEY")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Vector Database
    pinecone_environment: str = Field(..., env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(..., env="PINECONE_INDEX_NAME")
    
    # Application Settings
    app_name: str = Field("Enhanced CV Screening with Process Visualization", env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    fastapi_url: str = Field("http://localhost:8000", env="FASTAPI_URL")
    
    # WebSocket Settings
    websocket_host: str = Field("localhost", env="WEBSOCKET_HOST")
    websocket_port: int = Field(8001, env="WEBSOCKET_PORT")
    
    # Enhanced Process Explanation Settings
    explanation_detail_level: str = Field("moderate", env="EXPLANATION_DETAIL_LEVEL")
    human_intervention_enabled: bool = Field(True, env="HUMAN_INTERVENTION_ENABLED")
    real_time_updates: bool = Field(True, env="REAL_TIME_UPDATES")
    
    # Enhanced Analysis Features
    keyword_confidence_threshold: float = Field(0.75, env="KEYWORD_CONFIDENCE_THRESHOLD")
    scoring_explanation_enabled: bool = Field(True, env="SCORING_EXPLANATION_ENABLED")
    pattern_matching_enabled: bool = Field(True, env="PATTERN_MATCHING_ENABLED")
    industry_analysis_enabled: bool = Field(True, env="INDUSTRY_ANALYSIS_ENABLED")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
