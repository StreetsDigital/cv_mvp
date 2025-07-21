"""Enhanced CV Processor with New Skills Categories"""

import logging
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
import json
import re
from urllib.parse import urlparse

from ..models.cv_models import CandidateCV, JobRequirements, ComprehensiveScore
from ..models.digital_media.enhanced_skills_model import (
    ENHANCED_KEYWORDS, 
    INDUSTRY_EXPERTISE_INDICATORS,
    EnhancedScoringWeights
)

logger = logging.getLogger(__name__)

class EnhancedCVProcessor:
    """Enhanced CV processor with market-based skill categories"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"
        
        # Enhanced keyword mappings
        self.enhanced_keywords = ENHANCED_KEYWORDS
        self.industry_indicators = INDUSTRY_EXPERTISE_INDICATORS
        self.scoring_weights = EnhancedScoringWeights()
        
        # Performance metrics patterns
        self.performance_patterns = [
            r"ctr[:\s]*(\d+\.?\d*)%?",
            r"roas[:\s]*(\d+\.?\d*)",
            r"cpm[:\s]*\$?(\d+\.?\d*)",
            r"conversion rate[:\s]*(\d+\.?\d*)%?",
            r"engagement rate[:\s]*(\d+\.?\d*)%?",
            r"click-through rate[:\s]*(\d+\.?\d*)%?",
            r"return on ad spend[:\s]*(\d+\.?\d*)",
            r"cost per mille[:\s]*\$?(\d+\.?\d*)"
        ]
    
    async def process_enhanced_cv(
        self, 
        cv_text: str, 
        job_requirements: JobRequirements
    ) -> tuple[CandidateCV, ComprehensiveScore]:
        """Process CV with enhanced skill detection"""
        
        try:
            # Extract structured data using enhanced Claude prompt
            cv_data = await self._extract_enhanced_cv_data(cv_text)
            
            # Enhance with pattern matching for new skill categories
            cv_data = self._enhance_with_advanced_patterns(cv_data, cv_text)
            
            # Score the candidate with new criteria
            score = await self._score_enhanced_candidate(cv_data, job_requirements)
            
            logger.info(f"Enhanced CV processing completed for {cv_data.name}")
            return cv_data, score
            
        except Exception as e:
            logger.error(f"Enhanced CV processing failed: {e}")
            raise
    
    async def _extract_enhanced_cv_data(self, cv_text: str) -> CandidateCV:
        """Extract CV data using enhanced parsing prompt"""
        
        prompt = self._create_enhanced_parsing_prompt(cv_text)
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4000,  # Increased for more detailed extraction
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract and parse JSON
        response_text = message.content[0].text
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        json_str = response_text[json_start:json_end]
        
        # Parse and validate
        cv_dict = json.loads(json_str)
        return CandidateCV.model_validate(cv_dict)
    
    def _enhance_with_advanced_patterns(self, cv_data: CandidateCV, cv_text: str) -> CandidateCV:
        """Enhance CV data with advanced pattern matching"""
        
        cv_text_lower = cv_text.lower()
        
        # Detect SEO/SEM skills
        seo_skills = self._detect_skills_by_category(cv_text_lower, "seo_technical")
        if seo_skills:
            cv_data.seo_sem_expertise = seo_skills
        
        # Detect MarTech skills
        martech_skills = self._detect_skills_by_category(cv_text_lower, "martech_operations")
        if martech_skills:
            cv_data.martech_proficiency = martech_skills
        
        # Detect Advanced Analytics
        analytics_skills = self._detect_skills_by_category(cv_text_lower, "advanced_analytics")
        if analytics_skills:
            cv_data.advanced_analytics_skills = analytics_skills
        
        # Detect Affiliate Marketing
        affiliate_skills = self._detect_skills_by_category(cv_text_lower, "affiliate_marketing")
        if affiliate_skills:
            cv_data.affiliate_marketing_experience = affiliate_skills
        
        # Detect Influencer Marketing
        influencer_skills = self._detect_skills_by_category(cv_text_lower, "influencer_marketing")
        if influencer_skills:
            cv_data.influencer_marketing_experience = influencer_skills
        
        # Detect Remote Work Skills
        remote_skills = self._detect_skills_by_category(cv_text_lower, "remote_leadership")
        if remote_skills:
            cv_data.remote_collaboration_skills = remote_skills
        
        # Detect Industry Specialization
        industry_expertise = self._detect_industry_expertise(cv_text_lower)
        if industry_expertise:
            cv_data.industry_vertical_expertise = industry_expertise
        
        # Detect Executive Capabilities
        executive_skills = self._detect_executive_skills(cv_text_lower)
        if executive_skills:
            cv_data.executive_capabilities = executive_skills
        
        return cv_data
    
    def _detect_skills_by_category(self, cv_text_lower: str, category: str) -> List[str]:
        """Detect skills by category using keyword matching"""
        detected_skills = []
        
        if category in self.enhanced_keywords:
            keywords = self.enhanced_keywords[category]
            for keyword in keywords:
                if keyword in cv_text_lower:
                    detected_skills.append(keyword)
        
        return detected_skills
    
    def _detect_industry_expertise(self, cv_text_lower: str) -> List[str]:
        """Detect industry specialization"""
        detected_industries = []
        
        for industry, indicators in self.industry_indicators.items():
            for indicator in indicators:
                if indicator in cv_text_lower:
                    detected_industries.append(industry)
                    break  # One match per industry is enough
        
        return detected_industries
    
    def _detect_executive_skills(self, cv_text_lower: str) -> List[str]:
        """Detect executive-level capabilities"""
        executive_indicators = [
            "p&l responsibility", "profit and loss", "budget management",
            "strategic planning", "board presentation", "stakeholder management",
            "organizational development", "team leadership", "culture transformation",
            "market expansion", "business development", "investor relations"
        ]
        
        detected_executive = []
        for indicator in executive_indicators:
            if indicator in cv_text_lower:
                detected_executive.append(indicator)
        
        return detected_executive
    
    async def _score_enhanced_candidate(
        self, 
        cv_data: CandidateCV, 
        job_requirements: JobRequirements
    ) -> ComprehensiveScore:
        """Score candidate using enhanced criteria"""
        
        score = ComprehensiveScore()
        
        # Traditional scoring (60% weight)
        traditional_score = self._calculate_traditional_scores(cv_data, job_requirements)
        
        # Enhanced scoring (35% weight)
        enhanced_scores = self._calculate_enhanced_scores(cv_data, job_requirements)
        
        # Cultural/soft skills (5% weight)
        cultural_score = self._calculate_cultural_scores(cv_data, job_requirements)
        
        # Combine scores using enhanced weights
        weights = self.scoring_weights
        
        score.overall_match_score = (
            traditional_score["platform"] * weights.platform_expertise +
            traditional_score["creative"] * weights.creative_skills +
            traditional_score["analytics"] * weights.analytics_skills +
            traditional_score["campaign"] * weights.campaign_performance +
            enhanced_scores["seo_sem"] * weights.seo_sem_expertise +
            enhanced_scores["martech"] * weights.martech_operations +
            enhanced_scores["advanced_analytics"] * weights.advanced_analytics +
            enhanced_scores["industry"] * weights.industry_specialization +
            enhanced_scores["platform_leadership"] * weights.platform_leadership +
            enhanced_scores["sales_marketing"] * weights.sales_marketing_integration +
            cultural_score["remote"] * weights.remote_work_capability +
            cultural_score["executive"] * weights.executive_presence
        )
        
        # Set individual scores
        score.seo_sem_score = enhanced_scores["seo_sem"]
        score.martech_operations_score = enhanced_scores["martech"]
        score.advanced_analytics_score = enhanced_scores["advanced_analytics"]
        score.industry_specialization_score = enhanced_scores["industry"]
        score.platform_leadership_score = enhanced_scores["platform_leadership"]
        score.sales_marketing_integration_score = enhanced_scores["sales_marketing"]
        score.remote_capability_score = cultural_score["remote"]
        score.executive_readiness_score = cultural_score["executive"]
        
        return score
    
    def _calculate_traditional_scores(self, cv_data: CandidateCV, job_requirements: JobRequirements) -> Dict[str, float]:
        """Calculate traditional digital media scores"""
        scores = {
            "platform": 70.0,  # Default scores
            "creative": 70.0,
            "analytics": 70.0,
            "campaign": 70.0
        }
        
        # Implementation of traditional scoring logic would go here
        # (existing logic from previous digital_media_processor.py)
        
        return scores
    
    def _calculate_enhanced_scores(self, cv_data: CandidateCV, job_requirements: JobRequirements) -> Dict[str, float]:
        """Calculate scores for new skill categories"""
        scores = {}
        
        # SEO/SEM scoring
        scores["seo_sem"] = min(len(cv_data.seo_sem_expertise) * 20, 100.0)
        
        # MarTech scoring
        scores["martech"] = min(len(cv_data.martech_proficiency) * 25, 100.0)
        
        # Advanced Analytics scoring
        scores["advanced_analytics"] = min(len(cv_data.advanced_analytics_skills) * 30, 100.0)
        
        # Industry specialization
        scores["industry"] = min(len(cv_data.industry_vertical_expertise) * 40, 100.0)
        
        # Platform leadership
        scores["platform_leadership"] = min(len(cv_data.platform_leadership_experience) * 50, 100.0)
        
        # Sales-Marketing integration
        scores["sales_marketing"] = min(len(cv_data.sales_marketing_integration_skills) * 35, 100.0)
        
        return scores
    
    def _calculate_cultural_scores(self, cv_data: CandidateCV, job_requirements: JobRequirements) -> Dict[str, float]:
        """Calculate cultural fit and soft skill scores"""
        scores = {}
        
        # Remote work capability
        scores["remote"] = min(len(cv_data.remote_collaboration_skills) * 25, 100.0)
        
        # Executive presence
        scores["executive"] = min(len(cv_data.executive_capabilities) * 20, 100.0)
        
        return scores
    
    def _create_enhanced_parsing_prompt(self, cv_text: str) -> str:
        """Create enhanced parsing prompt with new skill categories"""
        return f"""
        Parse this CV for a digital media professional and extract comprehensive information including NEW SKILL CATEGORIES identified from market analysis. 
        Return ONLY valid JSON that matches the enhanced CandidateCV schema:
        
        {{
            "name": "string",
            "contact": {{
                "email": "string or null",
                "phone": "string or null",
                "linkedin": "string or null",
                "location": "string or null",
                "portfolio": "string or null"
            }},
            "experience": [{{
                "title": "string",
                "company": "string",
                "duration_months": "number",
                "description": "string or null",
                "skills_used": ["skill1", "skill2"],
                "start_date": "YYYY-MM-DD or null",
                "end_date": "YYYY-MM-DD or null",
                "achievements": [{{
                    "title": "string",
                    "description": "string",
                    "quantifiable_result": "string or null"
                }}]
            }}],
            "skills": ["skill1", "skill2"],
            "detailed_skills": [{{
                "skill_name": "string",
                "proficiency_level": "beginner|intermediate|advanced|expert",
                "years_experience": "number or null",
                "skill_category": "SEO|MarTech|Analytics|etc or null",
                "platform_specific": "Meta|Google|TikTok|etc or null",
                "industry_specific": "Healthcare|FinTech|etc or null"
            }}],
            
            // NEW ENHANCED SKILL CATEGORIES:
            "seo_sem_expertise": [
                "core web vitals", "schema markup", "technical seo", "local seo", 
                "google search console", "site speed optimization", "keyword research"
            ],
            "martech_proficiency": [
                "salesforce marketing cloud", "hubspot", "marketo", "pardot",
                "marketing automation", "lead scoring", "crm integration"
            ],
            "advanced_analytics_skills": [
                "sql", "python", "tableau", "power bi", "google analytics 4",
                "predictive modeling", "business intelligence", "data visualization"
            ],
            "affiliate_marketing_experience": [
                "commission tracking", "affiliate networks", "performance partnerships",
                "affiliate attribution", "partner management"
            ],
            "influencer_marketing_experience": [
                "creator management", "influencer roi", "ftc compliance",
                "micro influencers", "influencer contracts"
            ],
            "platform_leadership_experience": [
                "platform strategy", "head of platform", "platform optimization",
                "cross-platform integration", "platform training"
            ],
            "industry_vertical_expertise": [
                "healthcare", "financial services", "b2b saas", "ecommerce",
                "luxury brands", "automotive", "travel"
            ],
            "remote_collaboration_skills": [
                "virtual team management", "cross-timezone collaboration",
                "digital presentation", "async communication", "remote culture"
            ],
            "executive_capabilities": [
                "p&l responsibility", "strategic planning", "board presentation",
                "stakeholder management", "organizational development"
            ],
            "sales_marketing_integration_skills": [
                "crm management", "lead nurturing", "sales enablement",
                "revenue attribution", "customer lifecycle"
            ],
            
            "education": [{{
                "degree": "string",
                "institution": "string",
                "graduation_year": "number or null",
                "field_of_study": "string or null"
            }}],
            "certifications": [{{
                "name": "string",
                "issuer": "string",
                "issue_date": "YYYY-MM-DD or null",
                "expiry_date": "YYYY-MM-DD or null"
            }}],
            "total_experience_years": "number",
            "professional_summary": "string or null"
        }}
        
        CRITICAL EXTRACTION RULES FOR NEW CATEGORIES:
        
        1. SEO/SEM TECHNICAL SKILLS - Look for:
           - Core Web Vitals, schema markup, technical SEO audits
           - Site speed optimization, Google Search Console
           - Local SEO, keyword research, content optimization
        
        2. MARTECH/OPERATIONS - Look for:
           - Salesforce, HubSpot, Marketo, Pardot
           - Marketing automation, lead scoring, CRM integration
           - Workflow automation, drip campaigns
        
        3. ADVANCED ANALYTICS - Look for:
           - SQL, Python, R programming
           - Tableau, Power BI, advanced GA4
           - Predictive modeling, business intelligence
        
        4. AFFILIATE MARKETING - Look for:
           - Commission tracking, affiliate networks
           - Performance partnerships, affiliate attribution
        
        5. INFLUENCER MARKETING - Look for:
           - Creator management, influencer ROI
           - FTC compliance, influencer contracts
        
        6. PLATFORM LEADERSHIP - Look for:
           - "Head of [Platform]", platform strategy
           - Cross-platform integration, platform optimization
        
        7. INDUSTRY SPECIALIZATION - Look for:
           - Healthcare, HIPAA, FDA compliance
           - Financial services, B2B SaaS, ecommerce
           - Luxury brands, automotive, travel
        
        8. REMOTE WORK SKILLS - Look for:
           - Virtual team management, remote collaboration
           - Cross-timezone work, digital presentations
        
        9. EXECUTIVE CAPABILITIES - Look for:
           - P&L responsibility, strategic planning
           - Board presentations, stakeholder management
        
        10. SALES-MARKETING INTEGRATION - Look for:
            - CRM management, lead nurturing
            - Sales enablement, revenue attribution
        
        CV Text:
        {cv_text}
        """
