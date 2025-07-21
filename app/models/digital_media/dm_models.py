from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DigitalMediaRole(str, Enum):
    """Digital Media role categories"""
    CREATIVE_DESIGNER = "creative_designer"
    VIDEO_EDITOR = "video_editor"
    CONTENT_CREATOR = "content_creator"
    MEDIA_PLANNER = "media_planner"
    ACCOUNT_MANAGER = "account_manager"
    DATA_ANALYST = "data_analyst"
    AD_OPS_SPECIALIST = "ad_ops_specialist"
    CREATIVE_TECHNOLOGIST = "creative_technologist"
    GROWTH_MARKETER = "growth_marketer"
    BRAND_STRATEGIST = "brand_strategist"
    PERFORMANCE_MARKETER = "performance_marketer"
    SOCIAL_MEDIA_MANAGER = "social_media_manager"
    PROGRAMMATIC_SPECIALIST = "programmatic_specialist"

class PlatformExpertise(str, Enum):
    """Digital advertising platforms"""
    META_ADS = "meta_ads"
    GOOGLE_ADS = "google_ads"
    TIKTOK_ADS = "tiktok_ads"
    SNAPCHAT_ADS = "snapchat_ads"
    PINTEREST_ADS = "pinterest_ads"
    LINKEDIN_ADS = "linkedin_ads"
    TWITTER_ADS = "twitter_ads"
    AMAZON_ADS = "amazon_ads"
    YOUTUBE_ADS = "youtube_ads"
    PROGRAMMATIC_DSP = "programmatic_dsp"
    NATIVE_ADVERTISING = "native_advertising"
    INFLUENCER_PLATFORMS = "influencer_platforms"

class CreativeTools(str, Enum):
    """Creative software proficiency"""
    PHOTOSHOP = "photoshop"
    ILLUSTRATOR = "illustrator"
    AFTER_EFFECTS = "after_effects"
    PREMIERE_PRO = "premiere_pro"
    FIGMA = "figma"
    SKETCH = "sketch"
    CANVA = "canva"
    FINAL_CUT_PRO = "final_cut_pro"
    CINEMA_4D = "cinema_4d"
    BLENDER = "blender"
    INDESIGN = "indesign"
    DAVINCI_RESOLVE = "davinci_resolve"

class AnalyticsTools(str, Enum):
    """Analytics and measurement platforms"""
    GOOGLE_ANALYTICS = "google_analytics"
    FACEBOOK_ANALYTICS = "facebook_analytics"
    AMPLITUDE = "amplitude"
    MIXPANEL = "mixpanel"
    TABLEAU = "tableau"
    LOOKER = "looker"
    POWER_BI = "power_bi"
    ADOBE_ANALYTICS = "adobe_analytics"
    HOTJAR = "hotjar"
    CRAZY_EGG = "crazy_egg"
    OPTIMIZELY = "optimizely"
    VWO = "vwo"

class AgencyTier(str, Enum):
    """Agency classification for experience weighting"""
    TIER_1_GLOBAL = "tier_1_global"  # WPP, Omnicom, Publicis, IPG
    TIER_2_NETWORK = "tier_2_network"  # Havas, Dentsu, MDC Partners
    INDEPENDENT_AGENCY = "independent_agency"
    BOUTIQUE_AGENCY = "boutique_agency"
    IN_HOUSE_BRAND = "in_house_brand"
    STARTUP_INTERNAL = "startup_internal"
    FREELANCE = "freelance"

class CampaignType(str, Enum):
    """Campaign types for experience assessment"""
    BRAND_AWARENESS = "brand_awareness"
    PERFORMANCE_MARKETING = "performance_marketing"
    LEAD_GENERATION = "lead_generation"
    ECOMMERCE = "ecommerce"
    APP_INSTALL = "app_install"
    VIDEO_ADVERTISING = "video_advertising"
    SOCIAL_MEDIA = "social_media"
    PROGRAMMATIC = "programmatic"
    INFLUENCER = "influencer"
    NATIVE_CONTENT = "native_content"
    EMAIL_MARKETING = "email_marketing"
    AFFILIATE_MARKETING = "affiliate_marketing"

class DigitalMediaPortfolio(BaseModel):
    """Portfolio assessment for creative and strategic roles"""
    behance_url: Optional[HttpUrl] = None
    dribbble_url: Optional[HttpUrl] = None
    personal_website: Optional[HttpUrl] = None
    agency_work_samples: List[HttpUrl] = Field(default_factory=list)
    case_studies: List[str] = Field(default_factory=list)
    awards_recognition: List[str] = Field(default_factory=list)
    published_work: List[str] = Field(default_factory=list)
    
    # Portfolio quality scores (1-10)
    visual_design_quality: Optional[int] = Field(None, ge=1, le=10)
    strategic_thinking_quality: Optional[int] = Field(None, ge=1, le=10)
    brand_diversity_score: Optional[int] = Field(None, ge=1, le=10)
    innovation_score: Optional[int] = Field(None, ge=1, le=10)
    presentation_quality: Optional[int] = Field(None, ge=1, le=10)

class CampaignPerformance(BaseModel):
    """Campaign performance metrics"""
    campaign_name: str
    campaign_type: CampaignType
    budget_managed: Optional[float] = None
    duration_weeks: Optional[int] = None
    
    # Performance metrics
    ctr_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    cpm: Optional[float] = None
    cpv: Optional[float] = None
    roas: Optional[float] = None
    conversion_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    engagement_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    reach: Optional[int] = None
    impressions: Optional[int] = None
    
    # Brand metrics
    brand_lift_percentage: Optional[float] = None
    awareness_lift_percentage: Optional[float] = None
    
    platforms_used: List[PlatformExpertise] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)

class DigitalMediaCertification(BaseModel):
    """Digital media specific certifications"""
    name: str
    platform: PlatformExpertise
    certification_id: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_current: bool = True
    
    # Common certifications
    is_meta_blueprint: bool = False
    is_google_ads_certified: bool = False
    is_google_analytics_certified: bool = False
    is_amazon_dsp_certified: bool = False

class PlatformExperienceDetail(BaseModel):
    """Detailed platform experience"""
    platform: PlatformExpertise
    years_experience: float = Field(ge=0.0, le=20.0)
    proficiency_level: str = Field(..., regex=r'^(beginner|intermediate|advanced|expert)$')
    budget_managed_total: Optional[float] = None
    campaigns_managed: Optional[int] = None
    certifications: List[DigitalMediaCertification] = Field(default_factory=list)
    
    # Platform-specific features
    knows_advanced_features: bool = False
    api_experience: bool = False
    automation_experience: bool = False

class DigitalMediaExperience(BaseModel):
    """Enhanced experience model for digital media roles"""
    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    agency_tier: Optional[AgencyTier] = None
    duration_months: int = Field(..., ge=0, le=600)
    
    # Role categorization
    role_type: DigitalMediaRole
    is_client_facing: bool = False
    is_leadership_role: bool = False
    team_size_managed: Optional[int] = None
    
    # Campaign experience
    campaigns_managed: List[CampaignPerformance] = Field(default_factory=list)
    total_budget_managed: Optional[float] = None
    platform_expertise: List[PlatformExperienceDetail] = Field(default_factory=list)
    
    # Skills used
    creative_tools_used: List[CreativeTools] = Field(default_factory=list)
    analytics_tools_used: List[AnalyticsTools] = Field(default_factory=list)
    
    # Industry context
    industries_worked: List[str] = Field(default_factory=list)
    brand_clients: List[str] = Field(default_factory=list)
    
    # Cultural indicators
    mentions_trends: bool = False
    shows_data_driven_approach: bool = False
    demonstrates_creative_analytical_balance: bool = False

class DigitalMediaSkills(BaseModel):
    """Comprehensive digital media skills assessment"""
    
    # Platform expertise (weighted heavily)
    platform_skills: List[PlatformExperienceDetail] = Field(default_factory=list)
    
    # Creative skills
    creative_tools: List[CreativeTools] = Field(default_factory=list)
    design_skills: List[str] = Field(default_factory=list)
    video_production_skills: List[str] = Field(default_factory=list)
    
    # Analytical skills
    analytics_tools: List[AnalyticsTools] = Field(default_factory=list)
    data_analysis_skills: List[str] = Field(default_factory=list)
    attribution_modeling_experience: bool = False
    
    # Technical skills
    programming_languages: List[str] = Field(default_factory=list)
    web_technologies: List[str] = Field(default_factory=list)
    automation_tools: List[str] = Field(default_factory=list)
    
    # Strategic skills
    media_planning_experience: bool = False
    audience_segmentation_experience: bool = False
    competitive_analysis_experience: bool = False
    brand_strategy_experience: bool = False
    
    # Industry knowledge
    understands_privacy_changes: bool = False  # iOS14+, GDPR, etc.
    familiar_with_cookieless_future: bool = False
    knows_programmatic_ecosystem: bool = False
    
    # Cultural/trend awareness
    social_media_native: bool = False
    trend_identification_skills: bool = False
    gen_z_alpha_understanding: bool = False

class DigitalMediaCV(BaseModel):
    """Enhanced CV model specifically for digital media professionals"""
    
    # Basic information (inherits from base CV)
    name: str = Field(..., min_length=1, max_length=100)
    contact_email: str
    
    # Digital media specific fields
    portfolio: DigitalMediaPortfolio
    primary_role: DigitalMediaRole
    experience: List[DigitalMediaExperience] = Field(default_factory=list)
    skills: DigitalMediaSkills
    certifications: List[DigitalMediaCertification] = Field(default_factory=list)
    
    # Performance indicators
    total_budget_managed_career: Optional[float] = None
    number_of_campaigns_managed: Optional[int] = None
    average_campaign_performance: Optional[Dict[str, float]] = None
    
    # Industry reputation
    industry_awards: List[str] = Field(default_factory=list)
    speaking_engagements: List[str] = Field(default_factory=list)
    thought_leadership: List[str] = Field(default_factory=list)
    
    # Cultural fit indicators
    stays_current_with_trends: bool = False
    cross_functional_collaboration: bool = False
    startup_mentality: bool = False
    agency_experience_years: float = Field(0.0, ge=0.0)
    in_house_experience_years: float = Field(0.0, ge=0.0)
    
    @validator('total_budget_managed_career')
    def calculate_total_budget(cls, v, values):
        if 'experience' in values and values['experience']:
            total = sum(exp.total_budget_managed or 0 for exp in values['experience'])
            return total if total > 0 else None
        return v

class DigitalMediaJobRequirements(BaseModel):
    """Job requirements specific to digital media roles"""
    
    # Basic job info
    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    role_type: DigitalMediaRole
    
    # Platform requirements
    required_platforms: List[PlatformExpertise] = Field(default_factory=list)
    preferred_platforms: List[PlatformExpertise] = Field(default_factory=list)
    
    # Experience requirements
    min_years_experience: float = Field(0.0, ge=0.0)
    min_budget_managed: Optional[float] = None
    agency_experience_required: bool = False
    in_house_experience_required: bool = False
    client_facing_required: bool = False
    
    # Skill requirements
    required_creative_tools: List[CreativeTools] = Field(default_factory=list)
    required_analytics_tools: List[AnalyticsTools] = Field(default_factory=list)
    programming_skills_required: List[str] = Field(default_factory=list)
    
    # Certification requirements
    required_certifications: List[str] = Field(default_factory=list)
    preferred_certifications: List[str] = Field(default_factory=list)
    
    # Portfolio requirements
    portfolio_required: bool = True
    case_studies_required: bool = False
    specific_campaign_types: List[CampaignType] = Field(default_factory=list)
    
    # Industry requirements
    industry_experience_required: List[str] = Field(default_factory=list)
    brand_experience_required: List[str] = Field(default_factory=list)
    
    # Cultural requirements
    trend_awareness_required: bool = False
    startup_mentality_required: bool = False
    cross_functional_required: bool = False

class DigitalMediaScore(BaseModel):
    """Specialized scoring for digital media candidates"""
    
    # Overall score
    overall_match_score: float = Field(0.0, ge=0.0, le=100.0)
    
    # Category scores
    platform_expertise_score: float = Field(0.0, ge=0.0, le=100.0)
    portfolio_quality_score: float = Field(0.0, ge=0.0, le=100.0)
    campaign_performance_score: float = Field(0.0, ge=0.0, le=100.0)
    creative_skills_score: float = Field(0.0, ge=0.0, le=100.0)
    analytical_skills_score: float = Field(0.0, ge=0.0, le=100.0)
    agency_pedigree_score: float = Field(0.0, ge=0.0, le=100.0)
    cultural_fit_score: float = Field(0.0, ge=0.0, le=100.0)
    innovation_score: float = Field(0.0, ge=0.0, le=100.0)
    
    # Detailed analysis
    matched_platforms: List[PlatformExpertise] = Field(default_factory=list)
    missing_platforms: List[PlatformExpertise] = Field(default_factory=list)
    certification_gaps: List[str] = Field(default_factory=list)
    portfolio_strengths: List[str] = Field(default_factory=list)
    portfolio_weaknesses: List[str] = Field(default_factory=list)
    
    # Red flags specific to digital media
    outdated_platform_knowledge: List[str] = Field(default_factory=list)
    lacks_performance_metrics: bool = False
    no_portfolio_links: bool = False
    generic_social_media_experience: bool = False
    unfamiliar_with_privacy_changes: bool = False
    
    # Recommendations
    recommendation: str = Field(..., regex=r'^(strong_hire|hire|maybe|pass|strong_pass)$')
    interview_focus_areas: List[str] = Field(default_factory=list)
    skill_development_suggestions: List[str] = Field(default_factory=list)
