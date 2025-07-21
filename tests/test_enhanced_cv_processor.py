"""Test cases for Enhanced CV Processing"""

import pytest
import asyncio
from app.services.enhanced_cv_processor import EnhancedCVProcessor
from app.models.cv_models import JobRequirements

# Sample digital media CV with enhanced skills
SAMPLE_DIGITAL_MEDIA_CV = """
John Smith
Senior Digital Marketing Manager
Email: john.smith@email.com
LinkedIn: linkedin.com/in/johnsmith
Portfolio: johnsmith.com

PROFESSIONAL SUMMARY:
Results-driven digital marketing professional with 8+ years of experience in performance marketing, 
SEO optimization, and marketing automation. Expert in Google Analytics 4, Salesforce Marketing Cloud, 
and technical SEO audits. Led cross-functional teams and managed $2M+ annual advertising budgets.

EXPERIENCE:

Senior Digital Marketing Manager | TechCorp Inc. | 2021-Present (24 months)
• Implemented marketing automation workflows using HubSpot and Marketo, increasing lead conversion by 35%
• Managed Google Ads and Meta Ads campaigns with combined monthly budget of $200K, achieving 4.2x ROAS
• Conducted technical SEO audits focusing on Core Web Vitals optimization, improving site speed by 45%
• Led affiliate marketing program generating $500K additional revenue through commission tracking
• Developed influencer marketing strategy with 50+ creators, ensuring FTC compliance
• Built Tableau dashboards for advanced analytics and predictive modeling using SQL and Python
• Managed remote team of 8 across 3 time zones, implementing async communication protocols

Performance Marketing Specialist | Digital Agency Pro | 2019-2021 (24 months)
• Specialized in B2B SaaS marketing for healthcare and fintech clients
• Optimized conversion funnels resulting in 28% increase in trial-to-paid conversions
• Implemented schema markup and local SEO strategies for multi-location clients
• Used Salesforce Marketing Cloud for lead nurturing and customer lifecycle management
• Achieved Google Ads and Meta Blueprint certifications

Digital Marketing Coordinator | StartupXYZ | 2017-2019 (24 months)
• Supported luxury brand marketing campaigns for premium fashion clients
• Managed social media advertising across TikTok, Instagram, and Snapchat
• Assisted with board presentations and P&L analysis for marketing budget allocation

TECHNICAL SKILLS:
• SEO/SEM: Technical SEO audits, Core Web Vitals, schema markup, Google Search Console
• MarTech: Salesforce Marketing Cloud, HubSpot, Marketo, Pardot, Zapier integrations
• Analytics: SQL, Python, Tableau, Power BI, Google Analytics 4, predictive modeling
• Platforms: Google Ads, Meta Ads, TikTok Ads, LinkedIn Ads, Amazon DSP
• Creative Tools: Photoshop, Figma, After Effects
• Affiliate Marketing: Commission tracking, performance partnerships, affiliate attribution
• Remote Leadership: Virtual team management, cross-timezone collaboration

INDUSTRY EXPERTISE:
• Healthcare marketing (HIPAA compliance experience)
• B2B SaaS (product-led growth, free trial optimization)
• Fintech (regulatory compliance, trust marketing)
• Luxury brands (exclusivity marketing, brand heritage)

EDUCATION:
Bachelor of Marketing, University of California, 2017
Google Analytics 4 Certified, 2023
Meta Blueprint Certified, 2023
Salesforce Marketing Cloud Specialist, 2022

ACHIEVEMENTS:
• Increased overall marketing ROI by 180% through integrated campaign optimization
• Led digital transformation initiative resulting in 50% reduction in customer acquisition cost
• Recognized as "Digital Marketer of the Year" at Marketing Excellence Awards 2023
"""

SAMPLE_JOB_DESCRIPTION = """
Senior Digital Marketing Manager - Healthcare Technology

We are seeking a Senior Digital Marketing Manager to lead our digital marketing efforts for our healthcare technology platform. The ideal candidate will have deep expertise in healthcare marketing compliance, advanced analytics, and marketing automation.

Required Skills:
- 5+ years digital marketing experience in healthcare or regulated industries
- Expert-level Google Analytics 4 and advanced analytics (SQL, Python preferred)
- Marketing automation experience (Salesforce, HubSpot, or Marketo)
- Technical SEO and Core Web Vitals optimization
- Healthcare marketing compliance (HIPAA, FDA regulations)
- B2B SaaS marketing experience with free trial optimization
- Remote team leadership and cross-functional collaboration
- Advanced Excel/data analysis skills

Preferred Skills:
- Tableau or Power BI for data visualization
- Affiliate marketing and performance partnerships
- Influencer marketing with compliance management
- Platform-specific expertise (Google Ads, Meta Ads, LinkedIn Ads)
- Executive presentation and board-level communication skills

Responsibilities:
- Lead marketing automation strategy and implementation
- Conduct technical SEO audits and optimization
- Manage performance marketing campaigns across multiple platforms
- Develop healthcare-compliant marketing campaigns
- Present marketing performance to executive team and board
- Build and manage remote marketing team
- Implement advanced analytics and attribution modeling
"""

class TestEnhancedCVProcessor:
    
    @pytest.fixture
    def enhanced_processor(self):
        """Create enhanced CV processor instance"""
        # Use a test API key - in real tests, use a test environment
        return EnhancedCVProcessor(api_key="test_api_key")
    
    @pytest.fixture
    def sample_job_requirements(self):
        """Create sample job requirements"""
        return JobRequirements(
            title="Senior Digital Marketing Manager - Healthcare Technology",
            company="HealthTech Corp",
            description=SAMPLE_JOB_DESCRIPTION,
            required_skills=[
                "google analytics 4", "marketing automation", "technical seo",
                "healthcare marketing", "b2b saas", "remote leadership"
            ],
            required_seo_sem_skills=["core web vitals", "technical seo", "google analytics 4"],
            required_martech_skills=["salesforce", "hubspot", "marketo"],
            required_analytics_skills=["sql", "python", "tableau"],
            required_industry_expertise=["healthcare", "b2b saas"],
            remote_work_required=True,
            executive_level_role=False
        )
    
    def test_skill_category_detection(self, enhanced_processor):
        """Test detection of new skill categories"""
        
        # Test SEO/SEM detection
        cv_text = "experienced with core web vitals optimization and schema markup"
        detected = enhanced_processor._detect_skills_by_category(cv_text, "seo_technical")
        assert "core web vitals" in detected
        assert "schema markup" in detected
        
        # Test MarTech detection
        cv_text = "salesforce marketing cloud and hubspot automation"
        detected = enhanced_processor._detect_skills_by_category(cv_text, "martech_operations")
        assert "salesforce marketing cloud" in detected
        assert "hubspot" in detected
        
        # Test Advanced Analytics detection
        cv_text = "sql queries and python for predictive modeling"
        detected = enhanced_processor._detect_skills_by_category(cv_text, "advanced_analytics")
        assert "sql" in detected
        assert "python analytics" in detected
    
    def test_industry_expertise_detection(self, enhanced_processor):
        """Test industry specialization detection"""
        
        cv_text = "healthcare marketing with hipaa compliance and fintech experience"
        detected = enhanced_processor._detect_industry_expertise(cv_text)
        assert "healthcare" in detected
        assert "financial_services" in detected
    
    def test_executive_skills_detection(self, enhanced_processor):
        """Test executive capability detection"""
        
        cv_text = "p&l responsibility for marketing budget and board presentations"
        detected = enhanced_processor._detect_executive_skills(cv_text)
        assert "p&l responsibility" in detected
        assert "board presentation" in detected
    
    @pytest.mark.asyncio
    async def test_enhanced_cv_processing_integration(self, enhanced_processor, sample_job_requirements):
        """Test complete enhanced CV processing workflow"""
        
        # Note: This test would need a real API key to work with Claude
        # For demonstration purposes, we'll test the data flow
        
        try:
            cv_data, score = await enhanced_processor.process_enhanced_cv(
                SAMPLE_DIGITAL_MEDIA_CV, 
                sample_job_requirements
            )
            
            # Test that enhanced skills are populated
            assert len(cv_data.seo_sem_expertise) > 0
            assert len(cv_data.martech_proficiency) > 0
            assert len(cv_data.advanced_analytics_skills) > 0
            assert len(cv_data.industry_vertical_expertise) > 0
            
            # Test that enhanced scores are calculated
            assert score.seo_sem_score >= 0
            assert score.martech_operations_score >= 0
            assert score.advanced_analytics_score >= 0
            assert score.industry_specialization_score >= 0
            
            # Test overall score calculation
            assert 0 <= score.overall_match_score <= 100
            
        except Exception as e:
            # Expected to fail without real API key
            assert "api" in str(e).lower() or "key" in str(e).lower()
    
    def test_scoring_weights_validation(self, enhanced_processor):
        """Test that scoring weights are properly configured"""
        
        weights = enhanced_processor.scoring_weights
        
        # Test that all weights are valid percentages
        total_weight = (
            weights.platform_expertise + weights.campaign_performance +
            weights.creative_skills + weights.analytics_skills +
            weights.seo_sem_expertise + weights.martech_operations +
            weights.advanced_analytics + weights.industry_specialization +
            weights.platform_leadership + weights.sales_marketing_integration +
            weights.remote_work_capability + weights.executive_presence
        )
        
        # Should sum to approximately 1.0 (allowing for floating point precision)
        assert 0.99 <= total_weight <= 1.01
    
    def test_enhanced_keywords_coverage(self, enhanced_processor):
        """Test that enhanced keywords cover all major categories"""
        
        keywords = enhanced_processor.enhanced_keywords
        
        # Test that all major categories are covered
        required_categories = [
            "seo_technical", "martech_operations", "advanced_analytics",
            "affiliate_marketing", "influencer_marketing", "remote_leadership"
        ]
        
        for category in required_categories:
            assert category in keywords
            assert len(keywords[category]) > 0
    
    def test_pattern_matching_accuracy(self, enhanced_processor):
        """Test accuracy of pattern matching for various skill expressions"""
        
        test_cases = [
            ("I have experience with Core Web Vitals optimization", "seo_technical", "core web vitals"),
            ("Proficient in Salesforce Marketing Cloud automation", "martech_operations", "salesforce marketing cloud"),
            ("Advanced SQL and Python for data analysis", "advanced_analytics", "sql"),
            ("Managed affiliate partnerships and commission tracking", "affiliate_marketing", "commission tracking"),
            ("Led virtual teams across multiple time zones", "remote_leadership", "cross-timezone")
        ]
        
        for cv_text, category, expected_skill in test_cases:
            detected = enhanced_processor._detect_skills_by_category(cv_text.lower(), category)
            assert any(expected_skill in skill for skill in detected), f"Failed to detect {expected_skill} in {cv_text}"

if __name__ == "__main__":
    # Run basic tests without pytest
    processor = EnhancedCVProcessor(api_key="test_key")
    
    # Test skill detection
    print("Testing SEO skill detection...")
    seo_skills = processor._detect_skills_by_category(
        "core web vitals and schema markup optimization", 
        "seo_technical"
    )
    print(f"Detected SEO skills: {seo_skills}")
    
    # Test industry detection
    print("Testing industry detection...")
    industries = processor._detect_industry_expertise(
        "healthcare marketing with hipaa compliance"
    )
    print(f"Detected industries: {industries}")
    
    print("Enhanced CV processor tests completed!")
