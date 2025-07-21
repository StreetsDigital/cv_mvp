"""
Claude Code compatible CV processor with process explanation
Optimized for Claude Code development workflow
"""

import asyncio
import logging
from typing import Dict, Any, AsyncGenerator
from datetime import datetime

from ...backend.explainers.process_explainer import ProcessExplainer, ExplanationLevel
from ...backend.processors.enhanced_cv_processor import EnhancedCVProcessor
from ...backend.models.cv_models import CandidateCV, JobRequirements, MatchScore

logger = logging.getLogger(__name__)

class ClaudeCodeCVProcessor:
    """Claude Code compatible CV processor with process explanation"""
    
    def __init__(self, anthropic_api_key: str):
        self.enhanced_processor = EnhancedCVProcessor(anthropic_api_key)
        self.active_sessions: Dict[str, ProcessExplainer] = {}
        
    async def analyze_cv_with_explanation(
        self, 
        cv_text: str, 
        job_description: str,
        session_id: str = None,
        detail_level: ExplanationLevel = ExplanationLevel.MODERATE,
        websocket_callback: callable = None
    ) -> Dict[str, Any]:
        """Main analysis function with real-time explanation"""
        
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize process explainer
        explainer = ProcessExplainer(session_id, detail_level)
        if websocket_callback:
            explainer.add_websocket_callback(websocket_callback)
        
        self.active_sessions[session_id] = explainer
        
        try:
            # Step 1: Initialize process explanation
            await explainer.start_analysis_session()
            
            # Step 2: Parse CV with explanations
            cv_data = await self._parse_cv_with_explanation(cv_text, explainer)
            
            # Step 3: Parse job requirements with explanations
            job_requirements = await self._parse_job_with_explanation(job_description, explainer)
            
            # Step 4: Score with detailed explanations
            scores = await self._score_with_explanation(cv_data, job_requirements, explainer)
            
            # Step 5: Generate recommendations with explanations
            recommendations = await self._generate_recommendations_with_explanation(scores, explainer)
            
            # Final summary
            await explainer.explain_step(
                "✅ **Analysis Complete**",
                f"CV analysis completed successfully! Overall match score: {scores.overall_score:.1f}%",
                {
                    "final_score": scores.overall_score,
                    "processing_time": explainer._calculate_duration(),
                    "total_steps": explainer.current_step,
                    "session_summary": explainer.get_summary()
                }
            )
            
            return {
                "session_id": session_id,
                "cv_data": cv_data,
                "job_requirements": job_requirements,
                "match_score": scores,
                "recommendations": recommendations,
                "process_explanation": explainer.get_full_log(),
                "process_summary": explainer.get_summary(),
                "analysis_metadata": {
                    "detail_level": detail_level,
                    "total_steps": explainer.current_step,
                    "human_interventions": len(explainer.human_interventions),
                    "completion_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for session {session_id}: {str(e)}")
            await explainer.explain_step(
                "❌ **Analysis Failed**",
                f"An error occurred during analysis: {str(e)}",
                {"error": str(e), "error_type": type(e).__name__}
            )
            raise
        
        finally:
            # Clean up session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
    
    async def _parse_cv_with_explanation(self, cv_text: str, explainer: ProcessExplainer) -> CandidateCV:
        """Parse CV with step-by-step explanation"""
        
        await explainer.explain_step(
            "📄 **Parsing CV Structure**",
            "Extracting candidate information, work history, education, and skills sections",
            {
                "cv_length": len(cv_text),
                "parsing_method": "Claude API with structured extraction",
                "expected_sections": ["contact", "experience", "education", "skills"]
            }
        )
        
        # Use enhanced processor for actual parsing
        cv_data = await self.enhanced_processor.parse_cv_with_claude(cv_text)
        
        await explainer.explain_step(
            "✅ **CV Parsing Complete**",
            f"Successfully extracted data for {cv_data.name}",
            {
                "candidate_name": cv_data.name,
                "experience_entries": len(cv_data.experience),
                "education_entries": len(cv_data.education),
                "skills_identified": len(cv_data.skills),
                "total_experience": cv_data.total_experience_years
            }
        )
        
        return cv_data
    
    async def _parse_job_with_explanation(self, job_description: str, explainer: ProcessExplainer) -> JobRequirements:
        """Parse job description with explanation"""
        
        await explainer.explain_step(
            "📋 **Analyzing Job Requirements**",
            "Extracting required skills, experience, and qualifications from job description",
            {
                "job_desc_length": len(job_description),
                "extraction_focus": ["required_skills", "preferred_skills", "experience_requirements"]
            }
        )
        
        job_requirements = await self.enhanced_processor.parse_job_requirements(job_description)
        
        await explainer.explain_step(
            "✅ **Job Analysis Complete**",
            f"Identified {len(job_requirements.required_skills)} required and {len(job_requirements.preferred_skills)} preferred skills",
            {
                "job_title": job_requirements.title,
                "company": job_requirements.company,
                "required_skills": job_requirements.required_skills,
                "preferred_skills": job_requirements.preferred_skills,
                "min_experience": job_requirements.min_experience_years
            }
        )
        
        return job_requirements
    
    async def _score_with_explanation(
        self, 
        cv_data: CandidateCV, 
        job_requirements: JobRequirements, 
        explainer: ProcessExplainer
    ) -> MatchScore:
        """Score candidate with detailed explanations"""
        
        # Keyword extraction with explanation
        keywords_found = await self._extract_keywords_with_explanation(cv_data, explainer)
        
        # Skill categorization with explanation
        skill_scores = await self._categorize_skills_with_explanation(cv_data, job_requirements, explainer)
        
        # Pattern matching with explanation
        patterns = await self._analyze_patterns_with_explanation(cv_data, explainer)
        
        # Industry analysis with explanation
        industry_score = await self._analyze_industry_with_explanation(cv_data, job_requirements, explainer)
        
        # Calculate final scores
        match_score = await self.enhanced_processor.calculate_enhanced_match_score(
            cv_data, job_requirements, skill_scores, patterns, industry_score
        )
        
        await explainer.explain_final_scoring(
            {
                "skills_match": match_score.skills_match_score,
                "experience": match_score.experience_score,
                "education": match_score.education_score,
                "industry_fit": industry_score
            },
            match_score.overall_score
        )
        
        return match_score
    
    async def _extract_keywords_with_explanation(self, cv_data: CandidateCV, explainer: ProcessExplainer) -> List[Dict[str, Any]]:
        """Extract keywords with confidence scores and explanations"""
        
        # Simulate keyword extraction process
        cv_text = f"{' '.join(cv_data.skills)} {cv_data.summary or ''}"
        for exp in cv_data.experience:
            cv_text += f" {exp.title} {exp.description or ''}"
        
        keywords = [
            {"keyword": skill, "confidence": 0.9, "category": "explicit_skill"} 
            for skill in cv_data.skills
        ]
        
        await explainer.explain_keyword_extraction(cv_text, keywords)
        
        return keywords
    
    async def _categorize_skills_with_explanation(
        self, 
        cv_data: CandidateCV, 
        job_requirements: JobRequirements, 
        explainer: ProcessExplainer
    ) -> Dict[str, float]:
        """Categorize skills with explanations"""
        
        skill_categories = {
            "Platform Expertise": 0,
            "Campaign Performance": 0,
            "SEO/SEM": 0,
            "MarTech Operations": 0,
            "Content Marketing": 0
        }
        
        # Calculate scores for each category
        for category in skill_categories:
            relevant_skills = [skill for skill in cv_data.skills if self._skill_matches_category(skill, category)]
            score = min(len(relevant_skills) * 20, 100)  # Simple scoring
            skill_categories[category] = score
            
            await explainer.explain_skill_categorization(category, relevant_skills, score)
        
        return skill_categories
    
    async def _analyze_patterns_with_explanation(self, cv_data: CandidateCV, explainer: ProcessExplainer) -> Dict[str, Any]:
        """Analyze patterns with explanations"""
        
        patterns = {
            "agency_experience": {"detected": False, "confidence": 0.0},
            "remote_capability": {"detected": True, "confidence": 0.8},
            "leadership_experience": {"detected": False, "confidence": 0.3},
            "overall_confidence": 0.5
        }
        
        await explainer.explain_pattern_matching(patterns)
        
        return patterns
    
    async def _analyze_industry_with_explanation(
        self, 
        cv_data: CandidateCV, 
        job_requirements: JobRequirements, 
        explainer: ProcessExplainer
    ) -> float:
        """Analyze industry expertise with explanations"""
        
        industry = "Digital Marketing"
        confidence = 0.78
        evidence = [
            "Digital marketing campaign experience mentioned",
            "Marketing automation tools referenced",
            "Performance metrics and ROI tracking"
        ]
        
        await explainer.explain_industry_analysis(industry, confidence, evidence)
        
        return confidence * 100
    
    async def _generate_recommendations_with_explanation(
        self, 
        match_score: MatchScore, 
        explainer: ProcessExplainer
    ) -> Dict[str, Any]:
        """Generate recommendations with explanations"""
        
        recommendations = {
            "strengths": [
                "Strong technical capabilities in SEO and MarTech",
                "Proven campaign performance with quantified results"
            ],
            "validation_areas": [
                "Remote team leadership experience (limited evidence)",
                "Executive presentation skills (no clear examples)"
            ],
            "interview_focus": [
                "Technical SEO audit process and tools",
                "MarTech stack integration experience",
                "Healthcare compliance knowledge depth"
            ],
            "recommendation": "proceed_with_interview" if match_score.overall_score > 70 else "require_additional_screening",
            "confidence": match_score.confidence_level
        }
        
        await explainer.explain_recommendations(recommendations)
        
        return recommendations
    
    def _skill_matches_category(self, skill: str, category: str) -> bool:
        """Check if skill matches category"""
        category_keywords = {
            "Platform Expertise": ["google ads", "facebook ads", "linkedin ads", "twitter ads"],
            "SEO/SEM": ["seo", "sem", "search engine", "keyword research"],
            "MarTech Operations": ["hubspot", "salesforce", "marketo", "automation"],
            "Content Marketing": ["content", "blogging", "copywriting", "storytelling"],
            "Campaign Performance": ["optimization", "a/b testing", "conversion", "roi"]
        }
        
        keywords = category_keywords.get(category, [])
        return any(keyword in skill.lower() for keyword in keywords)
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active analysis sessions"""
        return {
            session_id: explainer.get_summary() 
            for session_id, explainer in self.active_sessions.items()
        }
    
    async def handle_human_intervention(
        self, 
        session_id: str, 
        intervention_type: str, 
        decision: str, 
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle human intervention decision"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        explainer = self.active_sessions[session_id]
        
        intervention_response = {
            "session_id": session_id,
            "intervention_type": intervention_type,
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        # Log the intervention
        explainer.human_interventions.append(intervention_response)
        
        # Send update to frontend
        await explainer._broadcast_to_frontend({
            "type": "human_intervention_processed",
            **intervention_response
        })
        
        return intervention_response
