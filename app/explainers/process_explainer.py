"""
Process Explanation Engine for Real-Time CV Analysis
Generates human-readable explanations for each AI processing step
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import re

logger = logging.getLogger(__name__)


class ProcessStep(str, Enum):
    """Enumeration of all CV analysis process steps"""
    # Initial Processing
    CV_PARSING = "cv_parsing"
    JOB_PARSING = "job_parsing"
    
    # Core Analysis
    SKILL_EXTRACTION = "skill_extraction"
    EXPERIENCE_ANALYSIS = "experience_analysis"
    EDUCATION_EVALUATION = "education_evaluation"
    
    # Advanced Analysis
    SEO_SEM_DETECTION = "seo_sem_detection"
    MARTECH_ANALYSIS = "martech_analysis"
    ANALYTICS_ASSESSMENT = "analytics_assessment"
    INDUSTRY_MATCHING = "industry_matching"
    LEADERSHIP_EVALUATION = "leadership_evaluation"
    REMOTE_CAPABILITY = "remote_capability"
    EXECUTIVE_READINESS = "executive_readiness"
    
    # Scoring
    SCORE_CALCULATION = "score_calculation"
    RECOMMENDATION_GENERATION = "recommendation_generation"
    
    # Final Steps
    FINAL_REVIEW = "final_review"
    REPORT_GENERATION = "report_generation"


class ExplanationContext(BaseModel):
    """Context information for generating explanations"""
    step: ProcessStep
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time: float = Field(..., description="Processing time in seconds")
    detected_items: List[str] = Field(default_factory=list)
    match_count: int = 0
    total_count: int = 0


class ProcessExplanation(BaseModel):
    """A human-readable explanation of a process step"""
    step_name: str
    headline: str
    detailed_explanation: str
    confidence_explanation: str
    evidence: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    technical_details: Optional[Dict[str, Any]] = None


class ProcessExplainer:
    """
    Generates human-readable explanations for CV analysis steps
    """
    
    def __init__(self):
        self.explanation_templates = self._initialize_templates()
        self.confidence_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
    
    def explain_step(self, context: ExplanationContext) -> ProcessExplanation:
        """
        Generate a human-readable explanation for a process step
        
        Args:
            context: Context information about the step
            
        Returns:
            ProcessExplanation with human-readable content
        """
        try:
            # Get the appropriate explanation method
            explainer_method = getattr(self, f"_explain_{context.step.value}", None)
            
            if explainer_method:
                return explainer_method(context)
            else:
                return self._generic_explanation(context)
                
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self._error_explanation(context, str(e))
    
    def _explain_cv_parsing(self, context: ExplanationContext) -> ProcessExplanation:
        """Explain CV parsing step"""
        cv_length = context.output_data.get("cv_length", 0)
        sections_found = context.output_data.get("sections_found", [])
        
        headline = "📄 Analyzing CV Structure"
        
        detailed = f"I'm reading through the CV to understand its structure and content. "
        detailed += f"The CV contains approximately {cv_length} words"
        
        if sections_found:
            detailed += f" organized into {len(sections_found)} sections: {', '.join(sections_found)}."
        else:
            detailed += "."
        
        confidence_exp = self._explain_confidence(context.confidence, "CV parsing")
        
        evidence = []
        if sections_found:
            evidence.append(f"Found {len(sections_found)} distinct sections")
            evidence.extend([f"✓ {section}" for section in sections_found[:5]])
        
        return ProcessExplanation(
            step_name="CV Parsing",
            headline=headline,
            detailed_explanation=detailed,
            confidence_explanation=confidence_exp,
            evidence=evidence,
            technical_details={
                "cv_length": cv_length,
                "sections": sections_found
            }
        )
    
    def _explain_skill_extraction(self, context: ExplanationContext) -> ProcessExplanation:
        """Explain skill extraction step"""
        skills_found = context.detected_items
        required_skills = context.input_data.get("required_skills", [])
        matches = context.match_count
        
        headline = "🔍 Identifying Technical Skills"
        
        detailed = f"I'm scanning the CV for technical skills and competencies. "
        detailed += f"Found {len(skills_found)} skills, with {matches} matching the job requirements."
        
        confidence_exp = self._explain_confidence(context.confidence, "skill matching")
        
        evidence = []
        if skills_found:
            evidence.append(f"Detected {len(skills_found)} skills:")
            evidence.extend([f"✓ {skill}" for skill in skills_found[:10]])
        
        suggestions = []
        missing_skills = set(required_skills) - set(skills_found)
        if missing_skills:
            suggestions.append(f"Missing skills: {', '.join(list(missing_skills)[:5])}")
        
        return ProcessExplanation(
            step_name="Skill Extraction",
            headline=headline,
            detailed_explanation=detailed,
            confidence_explanation=confidence_exp,
            evidence=evidence,
            suggestions=suggestions,
            technical_details={
                "total_skills": len(skills_found),
                "matching_skills": matches,
                "match_percentage": (matches / len(required_skills) * 100) if required_skills else 0
            }
        )
    
    def _explain_experience_analysis(self, context: ExplanationContext) -> ProcessExplanation:
        """Explain experience analysis step"""
        total_years = context.output_data.get("total_experience_years", 0)
        relevant_years = context.output_data.get("relevant_experience_years", 0)
        roles = context.output_data.get("roles_analyzed", [])
        
        headline = "💼 Evaluating Professional Experience"
        
        detailed = f"I'm analyzing the candidate's work history and experience. "
        detailed += f"Total experience: {total_years:.1f} years across {len(roles)} roles. "
        detailed += f"Relevant experience for this position: {relevant_years:.1f} years."
        
        confidence_exp = self._explain_confidence(context.confidence, "experience relevance")
        
        evidence = []
        if roles:
            evidence.append(f"Analyzed {len(roles)} professional roles:")
            for role in roles[:3]:
                evidence.append(f"✓ {role.get('title', 'Unknown')} at {role.get('company', 'Unknown')} ({role.get('duration', 'Unknown')})")
        
        return ProcessExplanation(
            step_name="Experience Analysis",
            headline=headline,
            detailed_explanation=detailed,
            confidence_explanation=confidence_exp,
            evidence=evidence,
            technical_details={
                "total_years": total_years,
                "relevant_years": relevant_years,
                "role_count": len(roles)
            }
        )
    
    def _explain_seo_sem_detection(self, context: ExplanationContext) -> ProcessExplanation:
        """Explain SEO/SEM expertise detection"""
        seo_keywords = context.detected_items
        campaigns = context.output_data.get("campaigns_mentioned", [])
        tools = context.output_data.get("tools_used", [])
        
        headline = "🔍 Analyzing SEO/SEM Expertise"
        
        detailed = f"I'm looking for evidence of SEO and SEM expertise. "
        if seo_keywords:
            detailed += f"Found {len(seo_keywords)} relevant SEO/SEM indicators. "
        if campaigns:
            detailed += f"The candidate mentions {len(campaigns)} specific campaigns. "
        if tools:
            detailed += f"Proficient in {len(tools)} SEO/SEM tools."
        
        confidence_exp = self._explain_confidence(context.confidence, "SEO/SEM expertise")
        
        evidence = []
        if seo_keywords:
            evidence.append("SEO/SEM Keywords detected:")
            evidence.extend([f"✓ {kw}" for kw in seo_keywords[:5]])
        if tools:
            evidence.append("Tools mentioned:")
            evidence.extend([f"✓ {tool}" for tool in tools[:3]])
        
        return ProcessExplanation(
            step_name="SEO/SEM Analysis",
            headline=headline,
            detailed_explanation=detailed,
            confidence_explanation=confidence_exp,
            evidence=evidence,
            technical_details={
                "keyword_count": len(seo_keywords),
                "tools": tools,
                "campaigns": len(campaigns)
            }
        )
    
    def _explain_score_calculation(self, context: ExplanationContext) -> ProcessExplanation:
        """Explain score calculation"""
        scores = context.output_data.get("component_scores", {})
        overall_score = context.output_data.get("overall_score", 0)
        
        headline = "📊 Calculating Match Scores"
        
        detailed = f"I'm combining all analysis results to calculate match scores. "
        detailed += f"Overall match score: {overall_score:.1%}. "
        
        # Find strongest and weakest areas
        if scores:
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            if sorted_scores:
                detailed += f"Strongest area: {sorted_scores[0][0]} ({sorted_scores[0][1]:.1%}). "
                if len(sorted_scores) > 1:
                    detailed += f"Area for improvement: {sorted_scores[-1][0]} ({sorted_scores[-1][1]:.1%})."
        
        confidence_exp = self._explain_confidence(context.confidence, "scoring accuracy")
        
        evidence = []
        for component, score in scores.items():
            evidence.append(f"{component}: {score:.1%}")
        
        return ProcessExplanation(
            step_name="Score Calculation",
            headline=headline,
            detailed_explanation=detailed,
            confidence_explanation=confidence_exp,
            evidence=evidence,
            technical_details={
                "overall_score": overall_score,
                "component_scores": scores
            }
        )
    
    def _explain_confidence(self, confidence: float, context: str) -> str:
        """Generate confidence explanation"""
        if confidence >= self.confidence_thresholds["high"]:
            return f"I'm highly confident ({confidence:.0%}) in this {context} based on clear evidence in the CV."
        elif confidence >= self.confidence_thresholds["medium"]:
            return f"I have moderate confidence ({confidence:.0%}) in this {context}. Some indicators are present but not comprehensive."
        elif confidence >= self.confidence_thresholds["low"]:
            return f"I have low confidence ({confidence:.0%}) in this {context}. Limited evidence was found."
        else:
            return f"I have very low confidence ({confidence:.0%}) in this {context}. Minimal evidence available."
    
    def _generic_explanation(self, context: ExplanationContext) -> ProcessExplanation:
        """Generic explanation for unhandled steps"""
        return ProcessExplanation(
            step_name=context.step.value.replace("_", " ").title(),
            headline=f"🔄 Processing {context.step.value.replace('_', ' ')}",
            detailed_explanation=f"Analyzing {context.step.value.replace('_', ' ')} with {context.confidence:.0%} confidence.",
            confidence_explanation=self._explain_confidence(context.confidence, "analysis"),
            evidence=[f"Processed in {context.processing_time:.2f} seconds"]
        )
    
    def _error_explanation(self, context: ExplanationContext, error: str) -> ProcessExplanation:
        """Explanation for errors"""
        return ProcessExplanation(
            step_name="Error in " + context.step.value.replace("_", " ").title(),
            headline="⚠️ Processing Issue Detected",
            detailed_explanation=f"I encountered an issue while {context.step.value.replace('_', ' ')}. I'll continue with the analysis.",
            confidence_explanation="Unable to complete this step with normal confidence levels.",
            suggestions=["This step may require manual review", "Results may be less accurate"],
            technical_details={"error": error}
        )
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize explanation templates"""
        return {
            "skill_found": "Found {skill} which matches the requirement for {requirement}",
            "experience_relevant": "{years} years of experience in {field} is relevant to this role",
            "education_match": "{degree} in {field} meets the educational requirements",
            "certification_found": "{certification} certification demonstrates expertise in {area}"
        }
    
    def format_for_display(self, explanation: ProcessExplanation, 
                          include_technical: bool = False) -> Dict[str, Any]:
        """
        Format explanation for display in UI
        
        Args:
            explanation: The process explanation
            include_technical: Whether to include technical details
            
        Returns:
            Formatted explanation for UI display
        """
        result = {
            "step_name": explanation.step_name,
            "headline": explanation.headline,
            "explanation": explanation.detailed_explanation,
            "confidence": explanation.confidence_explanation,
            "evidence": explanation.evidence,
            "suggestions": explanation.suggestions,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if include_technical and explanation.technical_details:
            result["technical"] = explanation.technical_details
            
        return result