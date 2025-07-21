"""Enhanced Digital Media Skills Model - Based on Market Analysis"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class SEOSEMSkills(str, Enum):
    """Technical SEO/SEM capabilities"""
    CORE_WEB_VITALS = "core_web_vitals"
    SCHEMA_MARKUP = "schema_markup"
    TECHNICAL_SEO_AUDIT = "technical_seo_audit"
    LOCAL_SEO = "local_seo"
    GOOGLE_SEARCH_CONSOLE = "google_search_console"
    SITE_SPEED_OPTIMIZATION = "site_speed_optimization"
    KEYWORD_RESEARCH = "keyword_research"
    CONTENT_OPTIMIZATION = "content_optimization"
    LINK_BUILDING = "link_building"
    MOBILE_SEO = "mobile_seo"

class MarTechStack(str, Enum):
    """Marketing Technology Stack"""
    SALESFORCE_MARKETING_CLOUD = "salesforce_marketing_cloud"
    HUBSPOT = "hubspot"
    MARKETO = "marketo"
    PARDOT = "pardot"
    ZAPIER = "zapier"
    LEAD_SCORING = "lead_scoring"
    MARKETING_AUTOMATION = "marketing_automation"
    CRM_INTEGRATION = "crm_integration"
    WORKFLOW_AUTOMATION = "workflow_automation"
    EMAIL_AUTOMATION = "email_automation"

class AdvancedAnalytics(str, Enum):
    """Advanced Analytics & BI Tools"""
    SQL = "sql"
    PYTHON = "python"
    R_PROGRAMMING = "r_programming"
    TABLEAU = "tableau"
    POWER_BI = "power_bi"
    GOOGLE_ANALYTICS_4 = "google_analytics_4"
    PREDICTIVE_MODELING = "predictive_modeling"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    DATA_VISUALIZATION = "data_visualization"
    STATISTICAL_ANALYSIS = "statistical_analysis"

class AffiliateMarketingSkills(str, Enum):
    """Affiliate Marketing Expertise"""
    COMMISSION_TRACKING = "commission_tracking"
    AFFILIATE_NETWORKS = "affiliate_networks"
    PERFORMANCE_PARTNERSHIPS = "performance_partnerships"
    AFFILIATE_ATTRIBUTION = "affiliate_attribution"
    FTC_COMPLIANCE = "ftc_compliance"
    AFFILIATE_RECRUITMENT = "affiliate_recruitment"
    COMMISSION_STRUCTURE = "commission_structure"
    PARTNER_MANAGEMENT = "partner_management"

class InfluencerMarketingSkills(str, Enum):
    """Influencer Marketing Operations"""
    CREATOR_MANAGEMENT = "creator_management"
    INFLUENCER_ROI = "influencer_roi"
    FTC_DISCLOSURE_COMPLIANCE = "ftc_disclosure_compliance"
    CONTRACT_NEGOTIATION = "contract_negotiation"
    MICRO_INFLUENCER_STRATEGY = "micro_influencer_strategy"
    MACRO_INFLUENCER_STRATEGY = "macro_influencer_strategy"
    INFLUENCER_PLATFORMS = "influencer_platforms"
    CONTENT_COLLABORATION = "content_collaboration"

class PlatformLeadershipSkills(str, Enum):
    """Platform-Specific Leadership"""
    PLATFORM_STRATEGY = "platform_strategy"
    ALGORITHM_UNDERSTANDING = "algorithm_understanding"
    PLATFORM_POLICY_COMPLIANCE = "platform_policy_compliance"
    CROSS_PLATFORM_INTEGRATION = "cross_platform_integration"
    PLATFORM_BETA_FEATURES = "platform_beta_features"
    PLATFORM_RELATIONSHIP_MANAGEMENT = "platform_relationship_management"
    PLATFORM_TRAINING = "platform_training"
    PLATFORM_OPTIMIZATION = "platform_optimization"

class IndustryVerticals(str, Enum):
    """Industry Specialization"""
    HEALTHCARE_LIFE_SCIENCES = "healthcare_life_sciences"
    FINANCIAL_SERVICES = "financial_services"
    B2B_SAAS = "b2b_saas"
    ECOMMERCE = "ecommerce"
    LUXURY_PREMIUM_BRANDS = "luxury_premium_brands"
    AUTOMOTIVE = "automotive"
    TRAVEL_HOSPITALITY = "travel_hospitality"
    EDUCATION = "education"
    GAMING = "gaming"
    CRYPTO_FINTECH = "crypto_fintech"

class RemoteWorkSkills(str, Enum):
    """Digital Collaboration & Remote Work"""
    VIRTUAL_CLIENT_MANAGEMENT = "virtual_client_management"
    CROSS_TIMEZONE_COLLABORATION = "cross_timezone_collaboration"
    DIGITAL_PRESENTATION = "digital_presentation"
    REMOTE_TEAM_LEADERSHIP = "remote_team_leadership"
    DISTRIBUTED_PROJECT_MANAGEMENT = "distributed_project_management"
    VIRTUAL_MEETING_FACILITATION = "virtual_meeting_facilitation"
    ASYNC_COMMUNICATION = "async_communication"
    REMOTE_CULTURE_BUILDING = "remote_culture_building"

class ExecutiveSkills(str, Enum):
    """C-Suite & Executive Capabilities"""
    PL_RESPONSIBILITY = "pl_responsibility"
    STRATEGIC_VISION = "strategic_vision"
    BOARD_PRESENTATION = "board_presentation"
    MARKET_EXPANSION = "market_expansion"
    ORGANIZATIONAL_DEVELOPMENT = "organizational_development"
    STAKEHOLDER_MANAGEMENT = "stakeholder_management"
    INVESTOR_RELATIONS = "investor_relations"
    CULTURE_TRANSFORMATION = "culture_transformation"

class SalesMarketingIntegration(str, Enum):
    """Sales-Marketing Hybrid Skills"""
    CRM_MANAGEMENT = "crm_management"
    LEAD_NURTURING = "lead_nurturing"
    SALES_ENABLEMENT = "sales_enablement"
    REVENUE_ATTRIBUTION = "revenue_attribution"
    CUSTOMER_LIFECYCLE = "customer_lifecycle"
    ACCOUNT_BASED_MARKETING = "account_based_marketing"
    SALES_FUNNEL_OPTIMIZATION = "sales_funnel_optimization"
    CUSTOMER_SUCCESS = "customer_success"

class EnhancedDigitalMediaSkills(BaseModel):
    """Comprehensive digital media skills based on market analysis"""
    
    # Existing skills (from previous model)
    platform_skills: List[str] = Field(default_factory=list)
    creative_tools: List[str] = Field(default_factory=list)
    analytics_tools: List[str] = Field(default_factory=list)
    
    # New skill categories
    seo_sem_skills: List[SEOSEMSkills] = Field(default_factory=list)
    martech_stack: List[MarTechStack] = Field(default_factory=list)
    advanced_analytics: List[AdvancedAnalytics] = Field(default_factory=list)
    affiliate_marketing: List[AffiliateMarketingSkills] = Field(default_factory=list)
    influencer_marketing: List[InfluencerMarketingSkills] = Field(default_factory=list)
    platform_leadership: List[PlatformLeadershipSkills] = Field(default_factory=list)
    industry_verticals: List[IndustryVerticals] = Field(default_factory=list)
    remote_work_skills: List[RemoteWorkSkills] = Field(default_factory=list)
    executive_skills: List[ExecutiveSkills] = Field(default_factory=list)
    sales_marketing_integration: List[SalesMarketingIntegration] = Field(default_factory=list)
    
    # Compliance and regulatory
    regulatory_compliance: List[str] = Field(default_factory=list)  # HIPAA, GDPR, FTC, etc.
    
    # Emerging technologies
    emerging_tech_familiarity: List[str] = Field(default_factory=list)  # AI/ML, Web3, AR/VR

class EnhancedScoringWeights(BaseModel):
    """Updated scoring weights based on market analysis"""
    
    # Core digital media skills (60%)
    platform_expertise: float = 0.20
    campaign_performance: float = 0.15
    creative_skills: float = 0.12
    analytics_skills: float = 0.13
    
    # New high-value skills (35%)
    seo_sem_expertise: float = 0.08
    martech_operations: float = 0.08
    advanced_analytics: float = 0.07
    industry_specialization: float = 0.05
    platform_leadership: float = 0.04
    sales_marketing_integration: float = 0.03
    
    # Soft skills and culture (5%)
    remote_work_capability: float = 0.03
    executive_presence: float = 0.02

# Market-specific keyword mappings
ENHANCED_KEYWORDS = {
    "seo_technical": [
        "core web vitals", "schema markup", "technical seo", "site speed",
        "google search console", "crawl errors", "sitemap", "robots.txt",
        "canonical tags", "meta descriptions", "title optimization"
    ],
    
    "martech_operations": [
        "salesforce marketing cloud", "hubspot workflows", "marketo automation",
        "pardot", "lead scoring", "drip campaigns", "nurture sequences",
        "marketing automation", "crm integration", "zapier"
    ],
    
    "advanced_analytics": [
        "sql", "python analytics", "r programming", "tableau", "power bi",
        "google analytics 4", "predictive modeling", "business intelligence",
        "data visualization", "statistical analysis", "cohort analysis"
    ],
    
    "affiliate_marketing": [
        "commission tracking", "affiliate networks", "commission junction",
        "shareasale", "performance partnerships", "affiliate attribution",
        "partner management", "affiliate recruitment"
    ],
    
    "influencer_marketing": [
        "creator management", "influencer roi", "ftc compliance",
        "influencer contracts", "micro influencers", "macro influencers",
        "creator platforms", "influencer analytics"
    ],
    
    "remote_leadership": [
        "virtual team management", "remote collaboration", "async communication",
        "cross-timezone", "distributed teams", "virtual presentations",
        "remote culture", "digital communication"
    ]
}

# Industry specialization indicators
INDUSTRY_EXPERTISE_INDICATORS = {
    "healthcare": [
        "hipaa compliance", "fda regulations", "healthcare marketing",
        "medical device", "pharmaceutical", "life sciences", "clinical trials"
    ],
    
    "financial_services": [
        "fintech", "banking regulations", "financial compliance",
        "investment marketing", "insurance marketing", "regulatory approval"
    ],
    
    "b2b_saas": [
        "product led growth", "free trial optimization", "saas metrics",
        "customer acquisition cost", "lifetime value", "churn reduction",
        "onboarding optimization", "feature adoption"
    ],
    
    "luxury_brands": [
        "luxury marketing", "premium positioning", "brand heritage",
        "exclusivity marketing", "high net worth", "luxury customer journey"
    ]
}
