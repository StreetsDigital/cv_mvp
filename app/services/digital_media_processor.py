import logging
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
import json
import re
from urllib.parse import urlparse

from ..models.digital_media.dm_models import (
    DigitalMediaCV, DigitalMediaJobRequirements, DigitalMediaScore,
    DigitalMediaRole, PlatformExpertise, CreativeTools, AnalyticsTools,
    AgencyTier, CampaignType, DigitalMediaPortfolio, CampaignPerformance
)

logger = logging.getLogger(__name__)

class DigitalMediaCVProcessor:
    """Specialized CV processor for digital media recruiting"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"
        
        # Digital media specific keywords and patterns
        self.platform_keywords = {
            PlatformExpertise.META_ADS: [
                "facebook ads", "meta ads", "instagram ads", "facebook advertising",
                "meta business manager", "ads manager", "facebook blueprint"
            ],
            PlatformExpertise.GOOGLE_ADS: [
                "google ads", "google adwords", "google advertising", "search ads",
                "display ads", "shopping ads", "youtube ads", "google ad grants"
            ],
            PlatformExpertise.TIKTOK_ADS: [
                "tiktok ads", "tiktok advertising", "tiktok business", "tiktok for business"
            ],
            PlatformExpertise.LINKEDIN_ADS: [
                "linkedin ads", "linkedin advertising", "linkedin campaign manager"
            ],
            PlatformExpertise.PROGRAMMATIC_DSP: [
                "dsp", "programmatic", "demand side platform", "real time bidding",
                "rtb", "dv360", "amazon dsp", "the trade desk", "adobe advertising cloud"
            ]
        }
        
        self.creative_tool_keywords = {
            CreativeTools.PHOTOSHOP: ["photoshop", "ps", "adobe photoshop"],
            CreativeTools.AFTER_EFFECTS: ["after effects", "ae", "adobe after effects"],
            CreativeTools.FIGMA: ["figma", "figma design"],
            CreativeTools.PREMIERE_PRO: ["premiere pro", "premiere", "adobe premiere"]
        }
        
        self.performance_metrics_patterns = [
            r"ctr[:\s]*(\d+\.?\d*)%?",
            r"roas[:\s]*(\d+\.?\d*)",
            r"cpm[:\s]*\$?(\d+\.?\d*)",
            r"conversion rate[:\s]*(\d+\.?\d*)%?",
            r"engagement rate[:\s]*(\d+\.?\d*)%?"
        ]
        
        self.agency_tier_mapping = {
            # Tier 1 Global Networks
            "wpp": AgencyTier.TIER_1_GLOBAL,
            "omnicom": AgencyTier.TIER_1_GLOBAL,
            "publicis": AgencyTier.TIER_1_GLOBAL,
            "interpublic": AgencyTier.TIER_1_GLOBAL,
            "ogilvy": AgencyTier.TIER_1_GLOBAL,
            "bbdo": AgencyTier.TIER_1_GLOBAL,
            "ddb": AgencyTier.TIER_1_GLOBAL,
            "saatchi": AgencyTier.TIER_1_GLOBAL,
            
            # Tier 2 Networks
            "havas": AgencyTier.TIER_2_NETWORK,
            "dentsu": AgencyTier.TIER_2_NETWORK,
            "mdc partners": AgencyTier.TIER_2_NETWORK,
            
            # Independent agencies (would need more comprehensive mapping)
            "independent": AgencyTier.INDEPENDENT_AGENCY
        }
    
    async def process_digital_media_cv(
        self, 
        cv_text: str, 
        job_requirements: DigitalMediaJobRequirements
    ) -> tuple[DigitalMediaCV, DigitalMediaScore]:
        """Process CV specifically for digital media roles"""
        
        try:
            # Extract structured data using Claude
            cv_data = await self._extract_digital_media_data(cv_text)
            
            # Enhance with pattern matching
            cv_data = self._enhance_with_pattern_matching(cv_data, cv_text)
            
            # Score the candidate
            score = await self._score_digital_media_candidate(cv_data, job_requirements)
            
            logger.info(f"Processed digital media CV for {cv_data.name}")
            return cv_data, score
            
        except Exception as e:
            logger.error(f"Digital media CV processing failed: {e}")
            raise
    
    async def _extract_digital_media_data(self, cv_text: str) -> DigitalMediaCV:
        """Extract digital media specific data using Claude"""
        
        prompt = self._create_digital_media_parsing_prompt(cv_text)
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract JSON from response
        response_text = message.content[0].text
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        json_str = response_text[json_start:json_end]
        
        # Parse and validate
        cv_dict = json.loads(json_str)
        return DigitalMediaCV.model_validate(cv_dict)
    
    def _enhance_with_pattern_matching(self, cv_data: DigitalMediaCV, cv_text: str) -> DigitalMediaCV:
        """Enhance extracted data with pattern matching"""
        
        cv_text_lower = cv_text.lower()
        
        # Extract portfolio URLs
        portfolio_urls = self._extract_portfolio_urls(cv_text)
        if portfolio_urls:
            if not cv_data.portfolio:
                cv_data.portfolio = DigitalMediaPortfolio()
            
            for url in portfolio_urls:
                if "behance" in url:
                    cv_data.portfolio.behance_url = url
                elif "dribbble" in url:
                    cv_data.portfolio.dribbble_url = url
                elif any(domain in url for domain in ["portfolio", "personal", "website"]):
                    cv_data.portfolio.personal_website = url
        
        # Detect performance metrics
        performance_metrics = self._extract_performance_metrics(cv_text)
        if performance_metrics and cv_data.experience:
            # Add metrics to most recent experience
            latest_exp = cv_data.experience[0]
            if not latest_exp.campaigns_managed:
                latest_exp.campaigns_managed = []
            
            # Create a sample campaign with extracted metrics
            campaign = CampaignPerformance(
                campaign_name="Performance Campaign",
                campaign_type=CampaignType.PERFORMANCE_MARKETING,
                **performance_metrics
            )
            latest_exp.campaigns_managed.append(campaign)
        
        # Detect platform expertise
        detected_platforms = self._detect_platform_expertise(cv_text_lower)
        if detected_platforms and cv_data.skills:
            for platform in detected_platforms:
                # Add to platform skills if not already present
                existing_platforms = [p.platform for p in cv_data.skills.platform_skills]
                if platform not in existing_platforms:
                    cv_data.skills.platform_skills.append({
                        "platform": platform,
                        "years_experience": 2.0,  # Default estimate
                        "proficiency_level": "intermediate"
                    })
        
        # Detect agency tier
        agency_tier = self._detect_agency_tier(cv_text_lower)
        if agency_tier and cv_data.experience:
            for exp in cv_data.experience:
                if not exp.agency_tier:
                    exp.agency_tier = agency_tier
                    break
        
        return cv_data
    
    def _extract_portfolio_urls(self, cv_text: str) -> List[str]:
        """Extract portfolio URLs from CV text"""
        url_pattern = r'https?://[^\s<>"]+'
        urls = re.findall(url_pattern, cv_text)
        
        portfolio_domains = [
            "behance.net", "dribbble.com", "portfolio", "personal",
            "website", "work", "projects"
        ]
        
        portfolio_urls = []
        for url in urls:
            if any(domain in url.lower() for domain in portfolio_domains):
                portfolio_urls.append(url)
        
        return portfolio_urls
    
    def _extract_performance_metrics(self, cv_text: str) -> Dict[str, float]:
        """Extract performance metrics from CV text"""
        metrics = {}
        
        for pattern in self.performance_metrics_patterns:
            matches = re.finditer(pattern, cv_text.lower())
            for match in matches:
                metric_name = match.group(0).split(':')[0].strip()
                metric_value = float(match.group(1))
                
                if "ctr" in metric_name:
                    metrics["ctr_percentage"] = metric_value
                elif "roas" in metric_name:
                    metrics["roas"] = metric_value
                elif "cpm" in metric_name:
                    metrics["cpm"] = metric_value
                elif "conversion" in metric_name:
                    metrics["conversion_rate"] = metric_value
                elif "engagement" in metric_name:
                    metrics["engagement_rate"] = metric_value
        
        return metrics
    
    def _detect_platform_expertise(self, cv_text_lower: str) -> List[PlatformExpertise]:
        """Detect platform expertise from CV text"""
        detected_platforms = []
        
        for platform, keywords in self.platform_keywords.items():
            if any(keyword in cv_text_lower for keyword in keywords):
                detected_platforms.append(platform)
        
        return detected_platforms
    
    def _detect_agency_tier(self, cv_text_lower: str) -> Optional[AgencyTier]:
        """Detect agency tier from company mentions"""
        for agency_name, tier in self.agency_tier_mapping.items():
            if agency_name in cv_text_lower:
                return tier
        return None
    
    async def _score_digital_media_candidate(
        self, 
        cv_data: DigitalMediaCV, 
        job_requirements: DigitalMediaJobRequirements
    ) -> DigitalMediaScore:
        """Score candidate for digital media role"""
        
        score = DigitalMediaScore()
        
        # Platform expertise scoring (30% weight)
        platform_score = self._score_platform_expertise(cv_data, job_requirements)
        score.platform_expertise_score = platform_score
        
        # Portfolio quality scoring (25% weight)
        portfolio_score = self._score_portfolio_quality(cv_data)
        score.portfolio_quality_score = portfolio_score
        
        # Campaign performance scoring (20% weight)
        performance_score = self._score_campaign_performance(cv_data)
        score.campaign_performance_score = performance_score
        
        # Creative skills scoring (10% weight)
        creative_score = self._score_creative_skills(cv_data, job_requirements)
        score.creative_skills_score = creative_score
        
        # Analytical skills scoring (10% weight)
        analytical_score = self._score_analytical_skills(cv_data, job_requirements)
        score.analytical_skills_score = analytical_score
        
        # Agency pedigree scoring (5% weight)
        agency_score = self._score_agency_pedigree(cv_data)
        score.agency_pedigree_score = agency_score
        
        # Calculate overall score
        score.overall_match_score = (
            platform_score * 0.30 +
            portfolio_score * 0.25 +
            performance_score * 0.20 +
            creative_score * 0.10 +
            analytical_score * 0.10 +
            agency_score * 0.05
        )
        
        # Set recommendation based on score
        if score.overall_match_score >= 85:
            score.recommendation = "strong_hire"
        elif score.overall_match_score >= 70:
            score.recommendation = "hire"
        elif score.overall_match_score >= 55:
            score.recommendation = "maybe"
        elif score.overall_match_score >= 40:
            score.recommendation = "pass"
        else:
            score.recommendation = "strong_pass"
        
        return score
    
    def _score_platform_expertise(
        self, 
        cv_data: DigitalMediaCV, 
        job_requirements: DigitalMediaJobRequirements
    ) -> float:
        """Score platform expertise match"""
        if not job_requirements.required_platforms:
            return 70.0  # Default score if no requirements
        
        candidate_platforms = [p.platform for p in cv_data.skills.platform_skills]
        required_platforms = job_requirements.required_platforms
        
        # Calculate match percentage
        matched_platforms = set(candidate_platforms) & set(required_platforms)
        match_percentage = len(matched_platforms) / len(required_platforms) * 100
        
        return min(match_percentage, 100.0)
    
    def _score_portfolio_quality(self, cv_data: DigitalMediaCV) -> float:
        """Score portfolio quality"""
        if not cv_data.portfolio:
            return 0.0
        
        score = 0.0
        
        # Portfolio presence (40 points)
        if cv_data.portfolio.behance_url or cv_data.portfolio.dribbble_url:
            score += 20.0
        if cv_data.portfolio.personal_website:
            score += 20.0
        
        # Quality scores (60 points)
        quality_scores = [
            cv_data.portfolio.visual_design_quality,
            cv_data.portfolio.strategic_thinking_quality,
            cv_data.portfolio.innovation_score
        ]
        
        valid_scores = [s for s in quality_scores if s is not None]
        if valid_scores:
            avg_quality = sum(valid_scores) / len(valid_scores)
            score += (avg_quality / 10) * 60
        
        return min(score, 100.0)
    
    def _score_campaign_performance(self, cv_data: DigitalMediaCV) -> float:
        """Score campaign performance metrics"""
        score = 0.0
        
        # Check if candidate has quantifiable performance metrics
        has_metrics = False
        for exp in cv_data.experience:
            if exp.campaigns_managed:
                for campaign in exp.campaigns_managed:
                    if (campaign.ctr_percentage or campaign.roas or 
                        campaign.conversion_rate or campaign.engagement_rate):
                        has_metrics = True
                        break
        
        if has_metrics:
            score += 50.0
        
        # Budget management experience
        if cv_data.total_budget_managed_career:
            if cv_data.total_budget_managed_career > 1000000:  # $1M+
                score += 30.0
            elif cv_data.total_budget_managed_career > 100000:  # $100K+
                score += 20.0
            else:
                score += 10.0
        
        # Number of campaigns
        if cv_data.number_of_campaigns_managed:
            if cv_data.number_of_campaigns_managed > 50:
                score += 20.0
            elif cv_data.number_of_campaigns_managed > 10:
                score += 15.0
            else:
                score += 5.0
        
        return min(score, 100.0)
    
    def _score_creative_skills(
        self, 
        cv_data: DigitalMediaCV, 
        job_requirements: DigitalMediaJobRequirements
    ) -> float:
        """Score creative skills match"""
        if not job_requirements.required_creative_tools:
            return 70.0  # Default if no requirements
        
        candidate_tools = cv_data.skills.creative_tools
        required_tools = job_requirements.required_creative_tools
        
        matched_tools = set(candidate_tools) & set(required_tools)
        match_percentage = len(matched_tools) / len(required_tools) * 100
        
        return min(match_percentage, 100.0)
    
    def _score_analytical_skills(
        self, 
        cv_data: DigitalMediaCV, 
        job_requirements: DigitalMediaJobRequirements
    ) -> float:
        """Score analytical skills match"""
        score = 0.0
        
        # Analytics tools proficiency
        if cv_data.skills.analytics_tools:
            score += 30.0
        
        # Attribution modeling experience
        if cv_data.skills.attribution_modeling_experience:
            score += 25.0
        
        # Data analysis skills
        if cv_data.skills.data_analysis_skills:
            score += 25.0
        
        # Programming skills for analysis
        if cv_data.skills.programming_languages:
            score += 20.0
        
        return min(score, 100.0)
    
    def _score_agency_pedigree(self, cv_data: DigitalMediaCV) -> float:
        """Score agency experience quality"""
        score = 0.0
        
        for exp in cv_data.experience:
            if exp.agency_tier == AgencyTier.TIER_1_GLOBAL:
                score += 40.0
                break
            elif exp.agency_tier == AgencyTier.TIER_2_NETWORK:
                score += 30.0
                break
            elif exp.agency_tier == AgencyTier.INDEPENDENT_AGENCY:
                score += 20.0
                break
        
        # Agency experience years
        if cv_data.agency_experience_years > 5:
            score += 30.0
        elif cv_data.agency_experience_years > 2:
            score += 20.0
        elif cv_data.agency_experience_years > 0:
            score += 10.0
        
        # Client-facing experience
        for exp in cv_data.experience:
            if exp.is_client_facing:
                score += 30.0
                break
        
        return min(score, 100.0)
    
    def _create_digital_media_parsing_prompt(self, cv_text: str) -> str:
        """Create specialized parsing prompt for digital media CVs"""
        return f"""
        Parse this CV for a digital media professional and extract comprehensive information. 
        Return ONLY valid JSON that matches the DigitalMediaCV schema:
        
        {{
            "name": "string",
            "contact_email": "string",
            "portfolio": {{
                "behance_url": "string or null",
                "dribbble_url": "string or null", 
                "personal_website": "string or null",
                "case_studies": ["case study 1", "case study 2"],
                "visual_design_quality": "number 1-10 or null",
                "strategic_thinking_quality": "number 1-10 or null",
                "innovation_score": "number 1-10 or null"
            }},
            "primary_role": "creative_designer|media_planner|performance_marketer|etc",
            "experience": [{{
                "title": "string",
                "company": "string",
                "duration_months": "number",
                "role_type": "performance_marketer|creative_designer|etc",
                "is_client_facing": "boolean",
                "total_budget_managed": "number or null",
                "platform_expertise": [{{
                    "platform": "meta_ads|google_ads|tiktok_ads|etc",
                    "years_experience": "number",
                    "proficiency_level": "beginner|intermediate|advanced|expert"
                }}],
                "campaigns_managed": [{{
                    "campaign_name": "string",
                    "campaign_type": "performance_marketing|brand_awareness|etc",
                    "ctr_percentage": "number or null",
                    "roas": "number or null",
                    "conversion_rate": "number or null"
                }}],
                "creative_tools_used": ["photoshop", "after_effects", "figma"],
                "analytics_tools_used": ["google_analytics", "facebook_analytics"]
            }}],
            "skills": {{
                "platform_skills": [{{
                    "platform": "meta_ads|google_ads|etc",
                    "years_experience": "number",
                    "proficiency_level": "beginner|intermediate|advanced|expert"
                }}],
                "creative_tools": ["photoshop", "figma", "after_effects"],
                "analytics_tools": ["google_analytics", "tableau"],
                "attribution_modeling_experience": "boolean",
                "understands_privacy_changes": "boolean",
                "social_media_native": "boolean"
            }},
            "certifications": [{{
                "name": "string",
                "platform": "meta_ads|google_ads|etc",
                "is_current": "boolean"
            }}],
            "agency_experience_years": "number",
            "in_house_experience_years": "number",
            "stays_current_with_trends": "boolean",
            "startup_mentality": "boolean"
        }}
        
        IMPORTANT EXTRACTION RULES:
        1. Look for portfolio URLs (Behance, Dribbble, personal websites)
        2. Extract specific platform experience (Meta Ads, Google Ads, TikTok, etc.)
        3. Find performance metrics (CTR, ROAS, conversion rates, engagement rates)
        4. Identify creative tools (Photoshop, After Effects, Figma, etc.)
        5. Recognize analytics tools (Google Analytics, Tableau, etc.)
        6. Assess agency vs in-house experience
        7. Look for budget management experience
        8. Identify certifications (Meta Blueprint, Google Ads certified, etc.)
        9. Check for cultural fit indicators (mentions trends, data-driven, etc.)
        10. Extract campaign types and performance
        
        CV Text:
        {cv_text}
        """
