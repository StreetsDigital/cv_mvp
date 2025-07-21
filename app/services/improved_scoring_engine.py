import logging
from typing import Dict, Any, List, Set, Optional
from ..models.cv_models import CandidateCV, JobRequirements, ComprehensiveScore
from ..models.api_models import CVAnalysisResponse

logger = logging.getLogger(__name__)

class ImprovedScoringEngine:
    """
    Enhanced CV scoring engine that prevents false matches by analyzing:
    1. Domain relevance
    2. Core skill alignment  
    3. Experience context
    4. Technical depth
    """
    
    def __init__(self):
        # Define distinct professional domains with their core skills
        self.domain_skills = {
            'software_engineering': {
                'core': ['programming', 'software development', 'coding', 'algorithms', 'data structures'],
                'languages': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust'],
                'frameworks': ['react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring'],
                'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp']
            },
            'mechanical_engineering': {
                'core': ['mechanical design', 'engineering design', 'cad', 'mechanical systems', 'product design'],
                'software': ['solidworks', 'autocad', 'inventor', 'catia', 'fusion 360', 'creo', 'ansys'],
                'specialties': ['cryogenic', 'rf connectors', 'microwave', 'machining', 'manufacturing', 'tooling'],
                'materials': ['materials science', 'metallurgy', 'composites', 'thermal analysis']
            },
            'digital_marketing': {
                'core': ['digital marketing', 'online advertising', 'programmatic', 'ad tech', 'marketing technology'],
                'platforms': ['google ads', 'facebook ads', 'google ad manager', 'doubleclick', 'prebid'],
                'analytics': ['google analytics', 'adobe analytics', 'tag manager', 'attribution'],
                'specialties': ['seo', 'sem', 'social media marketing', 'content marketing', 'email marketing']
            },
            'data_science': {
                'core': ['data science', 'machine learning', 'artificial intelligence', 'statistics', 'data analysis'],
                'languages': ['python', 'r', 'sql', 'scala', 'julia'],
                'tools': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'jupyter', 'tableau'],
                'techniques': ['regression', 'classification', 'clustering', 'deep learning', 'nlp']
            },
            'finance': {
                'core': ['finance', 'financial analysis', 'accounting', 'investment', 'risk management'],
                'tools': ['excel', 'bloomberg', 'reuters', 'matlab', 'sas', 'tableau'],
                'specialties': ['derivatives', 'portfolio management', 'equity research', 'fixed income', 'trading']
            }
        }
        
        # Keywords that indicate specific technical roles
        self.exclusion_keywords = {
            'engineering_physical': ['mechanical', 'electrical', 'civil', 'chemical', 'aerospace', 'biomedical'],
            'engineering_software': ['software engineer', 'developer', 'programmer', 'full stack', 'backend', 'frontend'],
            'medical': ['doctor', 'physician', 'nurse', 'medical', 'healthcare', 'clinical'],
            'legal': ['lawyer', 'attorney', 'legal counsel', 'paralegal', 'compliance', 'contract law'],
            'finance_specialized': ['investment banker', 'trader', 'analyst', 'portfolio manager', 'actuary']
        }
    
    def analyze_cv_comprehensive(self, cv: CandidateCV, job_requirements: JobRequirements) -> ComprehensiveScore:
        """
        Comprehensive CV analysis that prevents false matches
        """
        try:
            # Step 1: Domain Relevance Check (CRITICAL)
            domain_score = self._calculate_domain_relevance(cv, job_requirements)
            
            # Step 2: Core Skills Analysis
            skills_analysis = self._analyze_skills_deeply(cv, job_requirements)
            
            # Step 3: Experience Context Validation
            experience_analysis = self._analyze_experience_context(cv, job_requirements)
            
            # Step 4: Technical Depth Assessment
            technical_depth = self._assess_technical_depth(cv, job_requirements)
            
            # Step 5: Red Flag Detection
            red_flags = self._detect_red_flags(cv, job_requirements)
            
            # Step 6: Calculate Final Scores
            final_scores = self._calculate_comprehensive_scores(
                domain_score, skills_analysis, experience_analysis, technical_depth, red_flags
            )
            
            # Step 7: Generate Detailed Recommendations
            recommendation = self._generate_detailed_recommendation(final_scores, skills_analysis, red_flags)
            
            return ComprehensiveScore(
                overall_match_score=final_scores['overall'],
                confidence_score=final_scores['confidence'],
                skills_match_score=skills_analysis['core_match'],
                experience_relevance_score=experience_analysis['relevance'],
                technical_skills_score=technical_depth,
                domain_relevance_score=domain_score,
                matched_skills=skills_analysis['matched'],
                missing_skills=skills_analysis['missing'],
                skill_gaps=skills_analysis['gaps'],
                red_flags=red_flags,
                recommendation=recommendation,
                strengths=self._identify_strengths(cv, skills_analysis),
                concerns=self._identify_concerns(skills_analysis, red_flags)
            )
            
        except Exception as e:
            logger.error(f"Error in comprehensive CV analysis: {str(e)}")
            return self._create_error_response(cv.name)
    
    def _calculate_domain_relevance(self, cv: CandidateCV, job_req: JobRequirements) -> float:
        """
        Calculate domain relevance - prevents cross-domain false matches
        """
        # Identify job domain from title and requirements
        job_domain = self._identify_job_domain(job_req)
        
        # Identify candidate domain from experience and skills
        candidate_domains = self._identify_candidate_domains(cv)
        
        # Check for fundamental domain alignment
        if job_domain == 'unknown':
            return 70.0  # Neutral score for unclear job domains
        
        if job_domain in candidate_domains:
            return 100.0  # Perfect domain match
        
        # Check for related domains
        related_score = self._check_related_domains(job_domain, candidate_domains)
        if related_score > 0:
            return related_score
        
        # Check for transferable domains
        transferable_score = self._check_transferable_skills(job_domain, candidate_domains, cv, job_req)
        
        return transferable_score
    
    def _identify_job_domain(self, job_req: JobRequirements) -> str:
        """Identify the primary domain of the job"""
        title_lower = job_req.title.lower()
        desc_lower = job_req.description.lower()
        all_skills = job_req.required_skills + job_req.preferred_skills
        all_skills_lower = [skill.lower() for skill in all_skills]
        
        domain_scores = {}
        
        for domain, categories in self.domain_skills.items():
            score = 0
            
            # Check title
            for category_skills in categories.values():
                for skill in category_skills:
                    if skill in title_lower:
                        score += 3  # Title matches are strong indicators
                    if skill in desc_lower:
                        score += 1
                    if skill in all_skills_lower:
                        score += 2
            
            domain_scores[domain] = score
        
        # Return domain with highest score, or 'unknown' if no clear match
        if domain_scores:
            max_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[max_domain] >= 3:  # Minimum threshold
                return max_domain
        
        return 'unknown'
    
    def _identify_candidate_domains(self, cv: CandidateCV) -> List[str]:
        """Identify candidate's professional domains"""
        candidate_domains = []
        
        # Analyze job titles
        job_titles = [exp.title.lower() for exp in cv.experience]
        
        # Analyze skills
        all_skills = [skill.lower() for skill in cv.skills]
        
        for domain, categories in self.domain_skills.items():
            score = 0
            
            # Check job titles
            for title in job_titles:
                for category_skills in categories.values():
                    for skill in category_skills:
                        if skill in title:
                            score += 2
            
            # Check skills
            for skill in all_skills:
                for category_skills in categories.values():
                    if skill in category_skills:
                        score += 1
            
            # If candidate has significant experience in this domain
            if score >= 3:
                candidate_domains.append(domain)
        
        return candidate_domains
    
    def _check_related_domains(self, job_domain: str, candidate_domains: List[str]) -> float:
        """Check for related domain overlap"""
        related_domains = {
            'software_engineering': ['data_science'],
            'data_science': ['software_engineering'],
            'digital_marketing': [],  # Marketing is quite specialized
            'mechanical_engineering': [],  # Engineering is very specialized
            'finance': []  # Finance is very specialized
        }
        
        if job_domain in related_domains:
            for candidate_domain in candidate_domains:
                if candidate_domain in related_domains[job_domain]:
                    return 60.0  # Moderate score for related domains
        
        return 0.0
    
    def _check_transferable_skills(self, job_domain: str, candidate_domains: List[str], 
                                  cv: CandidateCV, job_req: JobRequirements) -> float:
        """Check for transferable skills across domains"""
        
        # Some roles have more transferable skills than others
        transferable_roles = {
            'project_management': 30.0,
            'team_leadership': 25.0,
            'business_analysis': 40.0,
            'sales': 35.0,
            'marketing': 30.0
        }
        
        # Check if the job is more of a general business role
        job_title_lower = job_req.title.lower()
        for role, score in transferable_roles.items():
            if role.replace('_', ' ') in job_title_lower:
                return score
        
        # Check candidate's leadership/management experience
        leadership_score = 0.0
        for exp in cv.experience:
            title_lower = exp.title.lower()
            if any(word in title_lower for word in ['manager', 'director', 'lead', 'head']):
                leadership_score += 5.0
        
        # Very low score for completely unrelated technical domains
        technical_domains = ['mechanical_engineering', 'software_engineering']
        if (job_domain in technical_domains and 
            not any(domain in technical_domains for domain in candidate_domains)):
            return min(20.0, leadership_score)  # Max 20% for completely different technical fields
        
        return min(40.0, leadership_score)
    
    def _analyze_skills_deeply(self, cv: CandidateCV, job_req: JobRequirements) -> Dict[str, Any]:
        """Deep analysis of skills alignment"""
        cv_skills_lower = set(skill.lower() for skill in cv.skills)
        required_skills_lower = set(skill.lower() for skill in job_req.required_skills)
        preferred_skills_lower = set(skill.lower() for skill in job_req.preferred_skills)
        
        # Find exact matches
        required_matches = cv_skills_lower.intersection(required_skills_lower)
        preferred_matches = cv_skills_lower.intersection(preferred_skills_lower)
        
        # Find partial/related matches
        related_matches = self._find_related_skill_matches(cv_skills_lower, required_skills_lower)
        
        # Calculate core match percentage
        total_required = len(required_skills_lower)
        if total_required == 0:
            core_match = 100.0
        else:
            exact_match_score = (len(required_matches) / total_required) * 70
            related_match_score = (len(related_matches) / total_required) * 20
            preferred_match_score = (len(preferred_matches) / len(preferred_skills_lower)) * 10 if preferred_skills_lower else 10
            core_match = min(100.0, exact_match_score + related_match_score + preferred_match_score)
        
        return {
            'core_match': core_match,
            'matched': list(required_matches.union(preferred_matches)),
            'missing': list(required_skills_lower - cv_skills_lower),
            'gaps': list(required_skills_lower - cv_skills_lower - related_matches),
            'related_matches': list(related_matches)
        }
    
    def _find_related_skill_matches(self, cv_skills: Set[str], required_skills: Set[str]) -> Set[str]:
        """Find skills that are related but not exact matches"""
        related_matches = set()
        
        # Define skill relationships
        skill_relationships = {
            'javascript': ['js', 'typescript', 'node.js'],
            'python': ['django', 'flask', 'fastapi', 'pandas'],
            'sql': ['mysql', 'postgresql', 'sqlite', 'database'],
            'aws': ['cloud', 'ec2', 's3', 'lambda'],
            'react': ['javascript', 'frontend', 'ui'],
            'machine learning': ['ai', 'data science', 'ml', 'artificial intelligence']
        }
        
        for required_skill in required_skills:
            for cv_skill in cv_skills:
                # Check if skills are related
                if required_skill in skill_relationships:
                    if cv_skill in skill_relationships[required_skill]:
                        related_matches.add(required_skill)
                elif cv_skill in skill_relationships:
                    if required_skill in skill_relationships[cv_skill]:
                        related_matches.add(required_skill)
        
        return related_matches
    
    def _analyze_experience_context(self, cv: CandidateCV, job_req: JobRequirements) -> Dict[str, Any]:
        """Analyze experience in context of job requirements"""
        
        # Check experience quantity
        experience_quantity_score = min(100.0, (cv.total_experience_years / job_req.min_experience_years) * 100) if job_req.min_experience_years > 0 else 100.0
        
        # Check experience relevance
        relevance_score = self._calculate_experience_relevance(cv, job_req)
        
        # Check career progression
        progression_score = self._analyze_career_progression(cv)
        
        # Combined experience score
        combined_score = (experience_quantity_score * 0.4 + relevance_score * 0.4 + progression_score * 0.2)
        
        return {
            'relevance': combined_score,
            'quantity_score': experience_quantity_score,
            'relevance_score': relevance_score,
            'progression_score': progression_score
        }
    
    def _calculate_experience_relevance(self, cv: CandidateCV, job_req: JobRequirements) -> float:
        """Calculate how relevant the candidate's experience is"""
        if not cv.experience:
            return 0.0
        
        job_title_keywords = job_req.title.lower().split()
        job_domain = self._identify_job_domain(job_req)
        
        relevance_score = 0.0
        total_weight = 0.0
        
        for exp in cv.experience:
            # Weight more recent/longer experiences higher
            weight = exp.duration_months / 12  # Convert to years for weighting
            total_weight += weight
            
            # Check title similarity
            title_similarity = self._calculate_title_similarity(exp.title.lower(), job_title_keywords)
            
            # Check domain alignment
            exp_domains = self._identify_experience_domain(exp)
            domain_alignment = 100.0 if job_domain in exp_domains else 0.0
            
            # Combined relevance for this experience
            exp_relevance = (title_similarity * 0.6 + domain_alignment * 0.4)
            relevance_score += exp_relevance * weight
        
        return relevance_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_title_similarity(self, exp_title: str, job_keywords: List[str]) -> float:
        """Calculate similarity between experience title and job title"""
        exp_words = set(exp_title.split())
        job_words = set(job_keywords)
        
        if not job_words:
            return 0.0
        
        common_words = exp_words.intersection(job_words)
        return (len(common_words) / len(job_words)) * 100
    
    def _identify_experience_domain(self, experience: 'Experience') -> List[str]:
        """Identify domain of a specific experience"""
        title_lower = experience.title.lower()
        company_lower = experience.company.lower()
        
        domains = []
        
        for domain, categories in self.domain_skills.items():
            score = 0
            for category_skills in categories.values():
                for skill in category_skills:
                    if skill in title_lower or skill in company_lower:
                        score += 1
            
            if score >= 1:
                domains.append(domain)
        
        return domains
    
    def _analyze_career_progression(self, cv: CandidateCV) -> float:
        """Analyze career progression pattern"""
        if len(cv.experience) < 2:
            return 50.0  # Neutral for limited experience
        
        progression_indicators = ['junior', 'senior', 'lead', 'principal', 'manager', 'director', 'vp', 'head']
        
        score = 50.0
        
        for i, exp in enumerate(cv.experience):
            title_lower = exp.title.lower()
            
            # Check for seniority indicators
            for j, indicator in enumerate(progression_indicators):
                if indicator in title_lower:
                    score += (j + 1) * 5  # Higher score for higher seniority
                    break
            
            # Check for increasing responsibility over time
            if i > 0:
                prev_exp = cv.experience[i-1]
                if exp.duration_months > prev_exp.duration_months:
                    score += 5.0  # Longer tenures suggest growth
        
        return min(100.0, score)
    
    def _assess_technical_depth(self, cv: CandidateCV, job_req: JobRequirements) -> float:
        """Assess technical depth and specialization"""
        # Count technical skills by category
        technical_skills = 0
        total_skills = len(cv.skills)
        
        if total_skills == 0:
            return 0.0
        
        # Count skills that appear in our domain definitions
        for skill in cv.skills:
            skill_lower = skill.lower()
            for domain, categories in self.domain_skills.items():
                for category_skills in categories.values():
                    if skill_lower in category_skills:
                        technical_skills += 1
                        break
        
        # Calculate depth vs breadth ratio
        depth_ratio = technical_skills / total_skills if total_skills > 0 else 0
        
        # Consider experience years for context
        experience_factor = min(1.0, cv.total_experience_years / 5)  # Cap at 5 years
        
        return min(100.0, depth_ratio * 100 * experience_factor)
    
    def _detect_red_flags(self, cv: CandidateCV, job_req: JobRequirements) -> List[str]:
        """Detect potential red flags in the match"""
        red_flags = []
        
        # Domain mismatch red flag
        job_domain = self._identify_job_domain(job_req)
        candidate_domains = self._identify_candidate_domains(cv)
        
        if job_domain != 'unknown' and job_domain not in candidate_domains:
            domain_names = {
                'mechanical_engineering': 'Mechanical Engineering',
                'software_engineering': 'Software Engineering',
                'digital_marketing': 'Digital Marketing/Ad Tech',
                'data_science': 'Data Science',
                'finance': 'Finance'
            }
            red_flags.append(f"Domain mismatch: Candidate has {domain_names.get(candidate_domains[0] if candidate_domains else 'Unknown', 'Unknown')} background, job requires {domain_names.get(job_domain, job_domain)}")
        
        # Skills gap red flag
        required_skills = set(skill.lower() for skill in job_req.required_skills)
        cv_skills = set(skill.lower() for skill in cv.skills)
        missing_skills = required_skills - cv_skills
        
        if len(missing_skills) > len(required_skills) * 0.5:  # Missing more than 50% of required skills
            red_flags.append(f"Major skills gap: Missing {len(missing_skills)} of {len(required_skills)} required skills")
        
        # Experience gap red flag
        if cv.total_experience_years < job_req.min_experience_years * 0.7:  # Less than 70% of required experience
            red_flags.append(f"Experience gap: {cv.total_experience_years} years vs {job_req.min_experience_years} required")
        
        # Career progression concerns
        if len(cv.experience) > 3:
            avg_tenure = sum(exp.duration_months for exp in cv.experience) / len(cv.experience) / 12
            if avg_tenure < 1.0:  # Less than 1 year average tenure
                red_flags.append("Job hopping pattern: Average tenure less than 1 year")
        
        return red_flags
    
    def _calculate_comprehensive_scores(self, domain_score: float, skills_analysis: Dict, 
                                      experience_analysis: Dict, technical_depth: float, 
                                      red_flags: List[str]) -> Dict[str, float]:
        """Calculate final comprehensive scores"""
        
        # Apply red flag penalties
        red_flag_penalty = len(red_flags) * 10  # 10 points per red flag
        
        # Domain score is CRITICAL - if it's very low, cap the overall score
        if domain_score < 30:
            max_possible_score = 40.0  # Cap at 40% for major domain mismatches
        elif domain_score < 50:
            max_possible_score = 70.0  # Cap at 70% for moderate domain mismatches
        else:
            max_possible_score = 100.0
        
        # Weighted calculation
        base_score = (
            domain_score * 0.35 +  # Domain is most important
            skills_analysis['core_match'] * 0.30 +  # Skills matching
            experience_analysis['relevance'] * 0.20 +  # Experience relevance
            technical_depth * 0.15  # Technical depth
        )
        
        # Apply penalties and caps
        final_score = max(0.0, min(max_possible_score, base_score - red_flag_penalty))
        
        # Confidence score based on data quality and alignment
        confidence = self._calculate_confidence_score(domain_score, skills_analysis, red_flags)
        
        return {
            'overall': round(final_score, 1),
            'confidence': confidence,
            'domain': domain_score,
            'base_score': base_score
        }
    
    def _calculate_confidence_score(self, domain_score: float, skills_analysis: Dict, red_flags: List[str]) -> int:
        """Calculate confidence in the assessment (1-10)"""
        confidence = 8  # Base confidence
        
        # Reduce confidence for domain mismatches
        if domain_score < 50:
            confidence -= 2
        elif domain_score < 70:
            confidence -= 1
        
        # Reduce confidence for skills gaps
        if skills_analysis['core_match'] < 50:
            confidence -= 2
        elif skills_analysis['core_match'] < 70:
            confidence -= 1
        
        # Reduce confidence for red flags
        confidence -= len(red_flags)
        
        return max(1, min(10, confidence))
    
    def _generate_detailed_recommendation(self, scores: Dict, skills_analysis: Dict, red_flags: List[str]) -> str:
        """Generate detailed recommendation"""
        overall_score = scores['overall']
        
        if red_flags:
            if overall_score < 30:
                return f"🔴 NOT RECOMMENDED - Major misalignment detected. {len(red_flags)} critical issues including: {red_flags[0]}"
            elif overall_score < 50:
                return f"🟡 PROCEED WITH CAUTION - {len(red_flags)} concerns identified. Consider only if role requirements are flexible."
        
        if overall_score >= 85:
            return "🟢 EXCELLENT MATCH - Strong alignment across all criteria. Recommend immediate interview."
        elif overall_score >= 75:
            return "🟢 GOOD MATCH - Solid candidate with minor gaps. Recommend interview."
        elif overall_score >= 65:
            return "🟡 MODERATE MATCH - Some gaps present. Consider for interview if pool is limited."
        elif overall_score >= 50:
            return "🟡 WEAK MATCH - Significant gaps. Consider only with extensive training."
        else:
            return "🔴 POOR MATCH - Not recommended. Major misalignment with role requirements."
    
    def _identify_strengths(self, cv: CandidateCV, skills_analysis: Dict) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        if cv.total_experience_years >= 5:
            strengths.append(f"Experienced professional ({cv.total_experience_years} years)")
        
        if len(skills_analysis['matched']) > 3:
            strengths.append(f"Strong skills match ({len(skills_analysis['matched'])} matched skills)")
        
        if len(cv.experience) >= 3:
            strengths.append("Diverse experience across multiple roles")
        
        return strengths
    
    def _identify_concerns(self, skills_analysis: Dict, red_flags: List[str]) -> List[str]:
        """Identify concerns beyond red flags"""
        concerns = []
        
        if len(skills_analysis['missing']) > 2:
            concerns.append(f"Missing {len(skills_analysis['missing'])} required skills")
        
        if skills_analysis['core_match'] < 60:
            concerns.append("Low skills alignment with job requirements")
        
        return concerns + red_flags
    
    def _create_error_response(self, candidate_name: str) -> ComprehensiveScore:
        """Create error response"""
        return ComprehensiveScore(
            overall_match_score=0.0,
            confidence_score=1,
            recommendation="Error analyzing CV - please review manually",
            red_flags=["Analysis error occurred"]
        )