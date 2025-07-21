"""
Enhanced CV Processor v1.1 with Real-Time Process Visualization
Integrates WebSocket updates and process explanations
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import time

from ..models.cv_models import CVData, JobRequirements
from ..models.digital_media.comprehensive_scoring import ComprehensiveScore
from ..services.enhanced_cv_processor import EnhancedCVProcessor
from ..services.websocket_manager import websocket_manager, ProcessUpdate
from ..explainers.process_explainer import (
    ProcessExplainer, ProcessStep, ExplanationContext
)

logger = logging.getLogger(__name__)


class EnhancedCVProcessorV11(EnhancedCVProcessor):
    """
    Enhanced CV Processor with real-time updates and explanations
    """
    
    def __init__(self, api_key: str, session_id: Optional[str] = None):
        super().__init__(api_key)
        self.session_id = session_id
        self.explainer = ProcessExplainer()
        self.process_history = []
        
    async def process_enhanced_cv_with_updates(
        self, 
        cv_text: str, 
        job_requirements: JobRequirements,
        session_id: str
    ) -> Tuple[CVData, ComprehensiveScore]:
        """
        Process CV with real-time updates via WebSocket
        
        Args:
            cv_text: Raw CV text
            job_requirements: Job requirements
            session_id: WebSocket session ID for updates
            
        Returns:
            Tuple of CVData and ComprehensiveScore
        """
        self.session_id = session_id
        
        try:
            # Step 1: Parse CV
            await self._process_step_with_update(
                step=ProcessStep.CV_PARSING,
                process_func=self._parse_cv_with_timing,
                args=(cv_text,),
                description="Parsing and understanding CV structure"
            )
            
            # Step 2: Parse Job Requirements
            await self._process_step_with_update(
                step=ProcessStep.JOB_PARSING,
                process_func=self._parse_job_with_timing,
                args=(job_requirements,),
                description="Analyzing job requirements"
            )
            
            # Step 3: Extract Skills
            skills_data = await self._process_step_with_update(
                step=ProcessStep.SKILL_EXTRACTION,
                process_func=self._extract_skills_with_timing,
                args=(cv_text, job_requirements),
                description="Identifying technical skills and competencies"
            )
            
            # Step 4: Analyze Experience
            experience_data = await self._process_step_with_update(
                step=ProcessStep.EXPERIENCE_ANALYSIS,
                process_func=self._analyze_experience_with_timing,
                args=(cv_text,),
                description="Evaluating professional experience"
            )
            
            # Step 5: Evaluate Education
            education_data = await self._process_step_with_update(
                step=ProcessStep.EDUCATION_EVALUATION,
                process_func=self._evaluate_education_with_timing,
                args=(cv_text,),
                description="Assessing educational background"
            )
            
            # Step 6: SEO/SEM Analysis
            seo_data = await self._process_step_with_update(
                step=ProcessStep.SEO_SEM_DETECTION,
                process_func=self._analyze_seo_sem_with_timing,
                args=(cv_text,),
                description="Detecting SEO/SEM expertise",
                requires_intervention=True,
                intervention_type="keyword_validation"
            )
            
            # Step 7: MarTech Analysis
            martech_data = await self._process_step_with_update(
                step=ProcessStep.MARTECH_ANALYSIS,
                process_func=self._analyze_martech_with_timing,
                args=(cv_text,),
                description="Analyzing marketing technology proficiency"
            )
            
            # Step 8: Advanced Analytics
            analytics_data = await self._process_step_with_update(
                step=ProcessStep.ANALYTICS_ASSESSMENT,
                process_func=self._assess_analytics_with_timing,
                args=(cv_text,),
                description="Evaluating data analytics capabilities"
            )
            
            # Step 9: Industry Matching
            industry_data = await self._process_step_with_update(
                step=ProcessStep.INDUSTRY_MATCHING,
                process_func=self._match_industry_with_timing,
                args=(cv_text, job_requirements),
                description="Matching industry experience"
            )
            
            # Step 10: Leadership Evaluation
            leadership_data = await self._process_step_with_update(
                step=ProcessStep.LEADERSHIP_EVALUATION,
                process_func=self._evaluate_leadership_with_timing,
                args=(cv_text,),
                description="Assessing leadership capabilities"
            )
            
            # Step 11: Calculate Scores
            cv_data, scores = await self._process_step_with_update(
                step=ProcessStep.SCORE_CALCULATION,
                process_func=self._calculate_comprehensive_score,
                args=(skills_data, experience_data, education_data, 
                      seo_data, martech_data, analytics_data, 
                      industry_data, leadership_data),
                description="Calculating comprehensive match scores",
                requires_intervention=True,
                intervention_type="score_adjustment"
            )
            
            # Step 12: Generate Recommendations
            recommendations = await self._process_step_with_update(
                step=ProcessStep.RECOMMENDATION_GENERATION,
                process_func=self._generate_recommendations_with_timing,
                args=(cv_data, scores),
                description="Creating interview recommendations"
            )
            
            # Step 13: Final Review
            await self._process_step_with_update(
                step=ProcessStep.FINAL_REVIEW,
                process_func=self._final_review_with_timing,
                args=(cv_data, scores),
                description="Performing final quality review"
            )
            
            # Add recommendations to scores
            scores.suggested_interview_questions = recommendations
            
            return cv_data, scores
            
        except Exception as e:
            logger.error(f"Error in enhanced CV processing: {e}")
            raise
    
    async def _process_step_with_update(
        self,
        step: ProcessStep,
        process_func: callable,
        args: tuple,
        description: str,
        requires_intervention: bool = False,
        intervention_type: Optional[str] = None
    ) -> Any:
        """
        Execute a process step with real-time updates
        
        Args:
            step: The process step
            process_func: Function to execute
            args: Arguments for the function
            description: Human-readable description
            requires_intervention: Whether human intervention is possible
            intervention_type: Type of intervention if applicable
            
        Returns:
            Result from process_func
        """
        start_time = time.time()
        
        # Send start update
        await self._send_process_update(
            step_name=step.value,
            status="started",
            confidence=0.0,
            explanation=f"Starting: {description}",
            requires_intervention=requires_intervention,
            intervention_type=intervention_type
        )
        
        try:
            # Execute the process function
            result, details = await process_func(*args)
            
            processing_time = time.time() - start_time
            
            # Calculate confidence based on results
            confidence = self._calculate_step_confidence(step, details)
            
            # Generate explanation
            context = ExplanationContext(
                step=step,
                input_data={"args": args},
                output_data=details,
                confidence=confidence,
                processing_time=processing_time,
                detected_items=details.get("detected_items", []),
                match_count=details.get("match_count", 0),
                total_count=details.get("total_count", 0)
            )
            
            explanation = self.explainer.explain_step(context)
            
            # Check if intervention is needed
            if requires_intervention and confidence < 0.7:
                intervention_result = await self._request_intervention(
                    step=step,
                    intervention_type=intervention_type,
                    context=details,
                    explanation=explanation
                )
                
                if intervention_result:
                    # Apply intervention changes
                    result = self._apply_intervention(result, intervention_result)
            
            # Send completion update
            await self._send_process_update(
                step_name=step.value,
                status="completed",
                confidence=confidence,
                explanation=explanation.detailed_explanation,
                details=self.explainer.format_for_display(explanation)
            )
            
            # Store in history
            self.process_history.append({
                "step": step,
                "result": result,
                "details": details,
                "explanation": explanation,
                "timestamp": datetime.utcnow()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in step {step.value}: {e}")
            
            # Send error update
            await self._send_process_update(
                step_name=step.value,
                status="failed",
                confidence=0.0,
                explanation=f"Error processing {description}: {str(e)}"
            )
            
            raise
    
    async def _send_process_update(
        self,
        step_name: str,
        status: str,
        confidence: float,
        explanation: str,
        details: Optional[Dict] = None,
        requires_intervention: bool = False,
        intervention_type: Optional[str] = None
    ):
        """Send process update via WebSocket"""
        if not self.session_id:
            return
        
        update = ProcessUpdate(
            step_name=step_name,
            status=status,
            confidence=confidence,
            explanation=explanation,
            details=details or {},
            requires_intervention=requires_intervention,
            intervention_type=intervention_type
        )
        
        await websocket_manager.send_process_update(self.session_id, update)
        
        # Small delay for UI updates
        await asyncio.sleep(0.1)
    
    async def _request_intervention(
        self,
        step: ProcessStep,
        intervention_type: str,
        context: Dict[str, Any],
        explanation: Any
    ) -> Optional[Dict[str, Any]]:
        """Request human intervention for a decision"""
        if not self.session_id:
            return None
        
        intervention_context = {
            "step": step.value,
            "current_values": context,
            "explanation": explanation.detailed_explanation,
            "suggestions": explanation.suggestions
        }
        
        return await websocket_manager.request_intervention(
            self.session_id,
            intervention_type,
            intervention_context
        )
    
    def _apply_intervention(self, result: Any, intervention: Dict[str, Any]) -> Any:
        """Apply human intervention to results"""
        # Implementation depends on intervention type
        # This is a simplified version
        if "adjustments" in intervention:
            for key, value in intervention["adjustments"].items():
                if hasattr(result, key):
                    setattr(result, key, value)
        
        return result
    
    def _calculate_step_confidence(self, step: ProcessStep, details: Dict) -> float:
        """Calculate confidence score for a processing step"""
        # Basic confidence calculation based on results
        if step == ProcessStep.SKILL_EXTRACTION:
            found = details.get("match_count", 0)
            total = details.get("total_count", 1)
            return min(found / total, 1.0) if total > 0 else 0.0
            
        elif step == ProcessStep.EXPERIENCE_ANALYSIS:
            relevant_years = details.get("relevant_experience_years", 0)
            return min(relevant_years / 5.0, 1.0)  # 5 years = 100% confidence
            
        elif step == ProcessStep.SEO_SEM_DETECTION:
            indicators = len(details.get("detected_items", []))
            return min(indicators / 10.0, 1.0)  # 10 indicators = 100% confidence
            
        else:
            # Default confidence based on whether we got results
            return 0.8 if details else 0.3
    
    # Wrapped processing functions with timing and details
    async def _parse_cv_with_timing(self, cv_text: str) -> Tuple[Dict, Dict]:
        """Parse CV and return with details"""
        # Simulate parsing
        sections = self._identify_sections(cv_text)
        
        result = {
            "raw_text": cv_text,
            "sections": sections
        }
        
        details = {
            "cv_length": len(cv_text.split()),
            "sections_found": list(sections.keys())
        }
        
        return result, details
    
    async def _parse_job_with_timing(self, job_requirements: JobRequirements) -> Tuple[Dict, Dict]:
        """Parse job requirements with details"""
        result = {
            "requirements": job_requirements
        }
        
        details = {
            "required_skills_count": len(job_requirements.required_skills),
            "preferred_skills_count": len(job_requirements.preferred_skills)
        }
        
        return result, details
    
    async def _extract_skills_with_timing(self, cv_text: str, 
                                         job_requirements: JobRequirements) -> Tuple[List[str], Dict]:
        """Extract skills with detailed matching"""
        # Use parent class method
        cv_data = await self.extract_cv_data_enhanced(cv_text)
        skills = cv_data.skills
        
        # Match against requirements
        required_matches = [s for s in skills if s in job_requirements.required_skills]
        preferred_matches = [s for s in skills if s in job_requirements.preferred_skills]
        
        details = {
            "detected_items": skills,
            "match_count": len(required_matches) + len(preferred_matches),
            "total_count": len(job_requirements.required_skills) + len(job_requirements.preferred_skills),
            "required_matches": required_matches,
            "preferred_matches": preferred_matches
        }
        
        return skills, details
    
    def _identify_sections(self, cv_text: str) -> Dict[str, str]:
        """Identify CV sections"""
        sections = {}
        section_patterns = {
            "experience": r"(?i)(work experience|professional experience|employment|experience)",
            "education": r"(?i)(education|academic|qualification)",
            "skills": r"(?i)(skills|technical skills|competencies)",
            "summary": r"(?i)(summary|profile|objective)",
            "certifications": r"(?i)(certification|certificate|credential)"
        }
        
        for section, pattern in section_patterns.items():
            import re
            if re.search(pattern, cv_text):
                sections[section] = "found"
                
        return sections
    
    # Additional wrapped methods would follow the same pattern...
    
    async def _analyze_experience_with_timing(self, cv_text: str) -> Tuple[Dict, Dict]:
        """Placeholder for experience analysis"""
        # This would call the actual experience analysis
        return {"experience": "analyzed"}, {"total_experience_years": 5.0, "relevant_experience_years": 3.5, "roles_analyzed": []}
    
    async def _evaluate_education_with_timing(self, cv_text: str) -> Tuple[Dict, Dict]:
        """Placeholder for education evaluation"""
        return {"education": "evaluated"}, {"degree_level": "Bachelor", "field": "Computer Science"}
    
    async def _analyze_seo_sem_with_timing(self, cv_text: str) -> Tuple[Dict, Dict]:
        """Placeholder for SEO/SEM analysis"""
        return {"seo_sem": "analyzed"}, {"detected_items": ["Google Ads", "SEO optimization"], "tools_used": ["Google Analytics"]}
    
    async def _analyze_martech_with_timing(self, cv_text: str) -> Tuple[Dict, Dict]:
        """Placeholder for MarTech analysis"""
        return {"martech": "analyzed"}, {"platforms": ["HubSpot", "Salesforce"]}
    
    async def _assess_analytics_with_timing(self, cv_text: str) -> Tuple[Dict, Dict]:
        """Placeholder for analytics assessment"""
        return {"analytics": "assessed"}, {"tools": ["Python", "SQL", "Tableau"]}
    
    async def _match_industry_with_timing(self, cv_text: str, job_requirements: JobRequirements) -> Tuple[Dict, Dict]:
        """Placeholder for industry matching"""
        return {"industry": "matched"}, {"match_score": 0.75, "industries": ["Tech", "SaaS"]}
    
    async def _evaluate_leadership_with_timing(self, cv_text: str) -> Tuple[Dict, Dict]:
        """Placeholder for leadership evaluation"""
        return {"leadership": "evaluated"}, {"team_size": 10, "management_years": 3}
    
    async def _calculate_comprehensive_score(self, *args) -> Tuple[Any, Dict]:
        """Calculate comprehensive scores"""
        # Placeholder - would integrate actual scoring
        from ..models.digital_media.comprehensive_scoring import ComprehensiveScore
        
        score = ComprehensiveScore(
            overall_match_score=0.85,
            skills_match_score=0.80,
            experience_relevance_score=0.75,
            seo_sem_score=0.70,
            martech_operations_score=0.65,
            advanced_analytics_score=0.60,
            industry_specialization_score=0.75,
            platform_leadership_score=0.70,
            remote_capability_score=0.80,
            executive_readiness_score=0.65,
            technical_skills_score=0.85,
            leadership_score=0.70,
            education_score=0.90,
            cultural_fit_score=0.75
        )
        
        cv_data = CVData(
            name="Placeholder Candidate",
            skills=["Python", "Marketing", "Analytics"],
            experience=[],
            education=[]
        )
        
        details = {
            "component_scores": {
                "Skills Match": score.skills_match_score,
                "Experience": score.experience_relevance_score,
                "SEO/SEM": score.seo_sem_score,
                "MarTech": score.martech_operations_score,
                "Analytics": score.advanced_analytics_score,
                "Industry": score.industry_specialization_score,
                "Leadership": score.leadership_score,
                "Education": score.education_score
            },
            "overall_score": score.overall_match_score
        }
        
        return (cv_data, score), details
    
    async def _generate_recommendations_with_timing(self, cv_data: Any, scores: Any) -> Tuple[List[str], Dict]:
        """Generate recommendations"""
        recommendations = [
            "Ask about specific SEO campaign results",
            "Discuss experience with marketing automation platforms",
            "Explore data analytics project examples"
        ]
        
        details = {
            "recommendation_count": len(recommendations),
            "based_on": "comprehensive analysis"
        }
        
        return recommendations, details
    
    async def _final_review_with_timing(self, cv_data: Any, scores: Any) -> Tuple[Dict, Dict]:
        """Final review step"""
        return {"status": "reviewed"}, {"quality_score": 0.9, "completeness": 0.95}