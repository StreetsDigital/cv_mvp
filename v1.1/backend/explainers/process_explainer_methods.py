    async def explain_keyword_extraction(self, text: str, keywords_found: List[Dict[str, Any]]):
        """Explain keyword extraction with human-in-loop option"""
        await self.explain_step(
            "🔤 **Keyword Extraction**",
            f"Analyzing text for {len(keywords_found)} industry-specific keywords",
            {
                "keywords_found": keywords_found,
                "text_sample": text[:200] + "..." if len(text) > 200 else text,
                "extraction_method": "Enhanced pattern matching with industry taxonomies",
                "total_keywords_detected": len(keywords_found),
                "avg_confidence": sum(kw.get('confidence', 0) for kw in keywords_found) / len(keywords_found) if keywords_found else 0
            },
            human_intervention_available=True
        )
    
    async def explain_skill_categorization(self, category: str, skills: List[str], score: float):
        """Explain skill categorization process"""
        await self.explain_step(
            f"📊 **Analyzing {category} Skills**",
            f"Evaluating {category.lower()} capabilities and experience",
            {
                "category": category,
                "skills_found": skills,
                "category_score": score,
                "evidence_strength": "strong" if score > 80 else "moderate" if score > 60 else "weak",
                "skill_count": len(skills)
            },
            confidence=score / 100,
            human_intervention_available=True
        )
    
    async def explain_scoring(self, category: str, score: float, reasoning: str, evidence: List[str] = None):
        """Explain scoring logic with transparency"""
        await self.explain_step(
            f"📊 **Scoring: {category}**",
            f"Calculated score: {score:.1f}% - {reasoning}",
            {
                "category": category,
                "score": score,
                "reasoning": reasoning,
                "evidence": evidence or [],
                "weight_in_overall": self._get_category_weight(category),
                "scoring_factors": self._get_scoring_factors(category)
            },
            confidence=score / 100
        )
    
    async def explain_pattern_matching(self, patterns: Dict[str, Any]):
        """Explain advanced pattern matching results"""
        await self.explain_step(
            "🔍 **Advanced Pattern Analysis**",
            "Using ML models to detect implicit skills and experience patterns",
            {
                "patterns_detected": patterns,
                "pattern_confidence": patterns.get('overall_confidence', 0),
                "agency_indicators": patterns.get('agency_experience', {}),
                "remote_indicators": patterns.get('remote_capability', {}),
                "leadership_indicators": patterns.get('leadership_experience', {})
            },
            confidence=patterns.get('overall_confidence', 0),
            human_intervention_available=True
        )
    
    async def explain_industry_analysis(self, industry: str, confidence: float, evidence: List[str]):
        """Explain industry expertise analysis"""
        await self.explain_step(
            f"🏥 **Industry Expertise Analysis**",
            f"Analyzing {industry} industry experience and compliance knowledge",
            {
                "industry": industry,
                "confidence": confidence,
                "evidence": evidence,
                "compliance_mentions": [e for e in evidence if 'compliance' in e.lower()],
                "industry_specific_metrics": [e for e in evidence if any(term in e.lower() for term in ['roi', 'kpi', 'conversion'])]
            },
            confidence=confidence,
            human_intervention_available=True
        )
    
    async def explain_final_scoring(self, breakdown: Dict[str, float], overall_score: float):
        """Explain final scoring calculation"""
        await self.explain_step(
            "🧮 **Calculating Weighted Scores**",
            f"Applying industry-optimized scoring weights to generate overall match score: {overall_score:.1f}%",
            {
                "score_breakdown": breakdown,
                "overall_score": overall_score,
                "calculation_method": "weighted_average",
                "top_strengths": [k for k, v in breakdown.items() if v > 80],
                "areas_for_improvement": [k for k, v in breakdown.items() if v < 60]
            },
            confidence=overall_score / 100
        )
    
    async def explain_recommendations(self, recommendations: Dict[str, Any]):
        """Explain generated recommendations"""
        await self.explain_step(
            "💡 **Generating Recommendations**",
            "Creating hiring recommendations and interview suggestions based on analysis",
            {
                "strengths": recommendations.get('strengths', []),
                "areas_for_validation": recommendations.get('validation_areas', []),
                "interview_focus": recommendations.get('interview_focus', []),
                "hiring_recommendation": recommendations.get('recommendation', 'pending'),
                "confidence_level": recommendations.get('confidence', 0)
            },
            confidence=recommendations.get('confidence', 0),
            human_intervention_available=True
        )
    
    async def request_human_intervention(self, intervention_type: str, data: Dict[str, Any]):
        """Request human intervention at specific points"""
        intervention = {
            "type": "human_intervention_required",
            "intervention_type": intervention_type,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "step": self.current_step,
            "data": data,
            "options": self._get_intervention_options(intervention_type)
        }
        
        self.human_interventions.append(intervention)
        await self._broadcast_to_frontend(intervention)
        
        return intervention
    
    def _get_category_weight(self, category: str) -> float:
        """Get weight for scoring category"""
        weights = {
            "Platform Expertise": 0.20,
            "Campaign Performance": 0.15,
            "SEO/SEM": 0.08,
            "MarTech Operations": 0.08,
            "Content Marketing": 0.10,
            "Social Media": 0.08,
            "Analytics": 0.10,
            "Project Management": 0.06,
            "Industry Experience": 0.10,
            "Communication": 0.05
        }
        return weights.get(category, 0.05)
    
    def _get_scoring_factors(self, category: str) -> List[str]:
        """Get factors considered in scoring for category"""
        factors_map = {
            "Platform Expertise": ["tool_proficiency", "certification_mentions", "hands_on_experience"],
            "Campaign Performance": ["quantified_results", "roi_metrics", "optimization_experience"],
            "SEO/SEM": ["technical_seo_knowledge", "keyword_strategy", "performance_tracking"],
            "MarTech Operations": ["automation_setup", "integration_experience", "workflow_optimization"]
        }
        return factors_map.get(category, ["experience_mentions", "skill_keywords", "context_relevance"])
    
    def _get_intervention_options(self, intervention_type: str) -> List[Dict[str, str]]:
        """Get available options for human intervention"""
        options_map = {
            "keyword_review": [
                {"value": "accept_all", "label": "✅ Accept all keywords"},
                {"value": "review_adjust", "label": "⚙️ Review and adjust"},
                {"value": "skip_category", "label": "❌ Skip this category"}
            ],
            "scoring_review": [
                {"value": "accept_score", "label": "✅ Accept calculated score"},
                {"value": "adjust_score", "label": "⚙️ Adjust score manually"},
                {"value": "add_evidence", "label": "📝 Add additional evidence"}
            ],
            "pattern_validation": [
                {"value": "confirm_patterns", "label": "✅ Confirm pattern matches"},
                {"value": "reject_patterns", "label": "❌ Reject pattern matches"},
                {"value": "partial_accept", "label": "⚙️ Accept some patterns"}
            ]
        }
        return options_map.get(intervention_type, [])
    
    async def _broadcast_to_frontend(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        for callback in self.websocket_callbacks:
            try:
                await callback(message)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
    
    def get_full_log(self) -> List[Dict[str, Any]]:
        """Get complete explanation log"""
        return self.explanation_log
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of the analysis process"""
        return {
            "session_id": self.session_id,
            "total_steps": len(self.explanation_log),
            "human_interventions": len(self.human_interventions),
            "detail_level": self.detail_level,
            "duration": self._calculate_duration(),
            "completion_status": "completed" if self.current_step > 10 else "in_progress"
        }
    
    def _calculate_duration(self) -> str:
        """Calculate analysis duration"""
        if not self.explanation_log:
            return "0:00"
        
        start_time = datetime.fromisoformat(self.explanation_log[0]['timestamp'])
        end_time = datetime.fromisoformat(self.explanation_log[-1]['timestamp'])
        duration = end_time - start_time
        
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        return f"{minutes}:{seconds:02d}"
