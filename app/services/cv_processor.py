import logging
import re
from typing import Dict, Any, List, Optional
from ..models.cv_models import CandidateCV, JobRequirements, ContactInfo, Education, Experience
from ..models.api_models import CVAnalysisResponse

logger = logging.getLogger(__name__)

class CVProcessor:
    """CV processing and analysis service"""
    
    def __init__(self):
        self.skill_keywords = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'tools': ['git', 'jenkins', 'jira', 'confluence', 'slack']
        }
    
    def extract_cv_data(self, cv_text: str) -> CandidateCV:
        """Extract structured data from CV text"""
        try:
            # Extract name (usually first line or after "Name:")
            name = self._extract_name(cv_text)
            
            # Extract contact information
            contact = self._extract_contact_info(cv_text)
            
            # Extract skills
            skills = self._extract_skills(cv_text)
            
            # Extract education
            education = self._extract_education(cv_text)
            
            # Extract experience
            experience = self._extract_experience(cv_text)
            
            # Calculate total experience
            total_experience = sum(exp.duration_months for exp in experience) / 12
            
            # Extract summary
            summary = self._extract_summary(cv_text)
            
            return CandidateCV(
                name=name,
                contact=contact,
                skills=skills,
                education=education,
                experience=experience,
                total_experience_years=round(total_experience, 1),
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error extracting CV data: {str(e)}")
            # Return minimal valid CV
            return CandidateCV(
                name="Unknown Candidate",
                contact=ContactInfo(),
                skills=[],
                education=[],
                experience=[],
                total_experience_years=0.0
            )
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name from CV text"""
        lines = text.strip().split('\n')
        
        # Look for common name patterns
        name_patterns = [
            r'Name[:\s]+([A-Za-z\s]+)',
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        # Fallback: use first non-empty line if it looks like a name
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) <= 4 and all(word.replace('-', '').isalpha() for word in line.split()):
                return line
        
        return "Unknown Candidate"
    
    def _extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'[\+]?[1-9]?[0-9]{7,14}'
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9\-]+'
        
        email_match = re.search(email_pattern, text)
        phone_match = re.search(phone_pattern, text)
        linkedin_match = re.search(linkedin_pattern, text)
        
        return ContactInfo(
            email=email_match.group() if email_match else None,
            phone=phone_match.group() if phone_match else None,
            linkedin=f"https://{linkedin_match.group()}" if linkedin_match else None,
            location=self._extract_location(text)
        )
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location information"""
        location_patterns = [
            r'Location[:\s]+([A-Za-z\s,]+)',
            r'Address[:\s]+([A-Za-z\s,]+)',
            r'([A-Z][a-z]+,\s*[A-Z]{2})',
            r'([A-Z][a-z]+\s*,\s*[A-Z][a-z]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from CV text"""
        text_lower = text.lower()
        found_skills = set()
        
        # Extract from all skill categories
        for category, skills in self.skill_keywords.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills.add(skill.lower())
        
        # Look for skills sections
        skills_section_pattern = r'(?:skills?|technologies?|technical skills?)[:\s]+(.*?)(?:\n\s*\n|\n[A-Z]|$)'
        skills_match = re.search(skills_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if skills_match:
            skills_text = skills_match.group(1)
            # Split by common delimiters
            skills_list = re.split(r'[,;•\-\n\t]+', skills_text)
            for skill in skills_list:
                skill = skill.strip()
                if skill and len(skill) < 30:  # Reasonable skill name length
                    found_skills.add(skill.lower())
        
        return list(found_skills)
    
    def _extract_education(self, text: str) -> List[Education]:
        """Extract education information"""
        education_list = []
        
        # Look for education section
        education_pattern = r'(?:education|academic|qualifications?)[:\s]+(.*?)(?:\n\s*\n|\n[A-Z]|$)'
        education_match = re.search(education_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if education_match:
            education_text = education_match.group(1)
            
            # Extract degree and institution patterns
            degree_patterns = [
                r'(Bachelor|Master|PhD|MBA|BS|MS|BA|MA)[^,\n]+(?:,|\n|\s+)(.*?)(?:\d{4}|\n|$)',
                r'([A-Za-z\s]+(?:degree|certification))[^,\n]*(?:,|\n|\s+)(.*?)(?:\d{4}|\n|$)'
            ]
            
            for pattern in degree_patterns:
                matches = re.finditer(pattern, education_text, re.IGNORECASE)
                for match in matches:
                    degree = match.group(1).strip()
                    institution = match.group(2).strip()
                    
                    if degree and institution:
                        education_list.append(Education(
                            degree=degree,
                            institution=institution,
                            graduation_year=self._extract_year(match.group(0))
                        ))
        
        return education_list
    
    def _extract_experience(self, text: str) -> List[Experience]:
        """Extract work experience"""
        experience_list = []
        
        # Look for experience section
        experience_pattern = r'(?:experience|employment|work history|professional)[:\s]+(.*?)(?:\n\s*\n|\n[A-Z]|$)'
        experience_match = re.search(experience_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if experience_match:
            experience_text = experience_match.group(1)
            
            # Extract job entries
            job_pattern = r'([A-Za-z\s]+)\s*(?:at|@)\s*([A-Za-z\s&,.]+)(?:\s*[-–]\s*(\d{1,2})\s*(?:years?|months?|yrs?))?'
            matches = re.finditer(job_pattern, experience_text, re.IGNORECASE)
            
            for match in matches:
                title = match.group(1).strip()
                company = match.group(2).strip()
                duration_text = match.group(3) if match.group(3) else "12"
                
                try:
                    duration_months = int(duration_text) if duration_text.isdigit() else 12
                except:
                    duration_months = 12
                
                if title and company:
                    experience_list.append(Experience(
                        title=title,
                        company=company,
                        duration_months=duration_months,
                        description=None,
                        skills_used=[]
                    ))
        
        return experience_list
    
    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract summary or objective"""
        summary_patterns = [
            r'(?:summary|objective|profile|about)[:\s]+(.*?)(?:\n\s*\n|\n[A-Z]|$)',
            r'(?:professional summary|career objective)[:\s]+(.*?)(?:\n\s*\n|\n[A-Z]|$)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                if len(summary) > 50:  # Ensure it's a meaningful summary
                    return summary
        
        return None
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        year_pattern = r'\b(19|20)\d{2}\b'
        match = re.search(year_pattern, text)
        if match:
            year = int(match.group())
            if 1950 <= year <= 2030:
                return year
        return None
    
    def analyze_cv_match(self, cv: CandidateCV, job_requirements: JobRequirements) -> CVAnalysisResponse:
        """Analyze CV match against job requirements"""
        try:
            # Calculate skills match
            skills_score = self._calculate_skills_match(cv.skills, job_requirements.required_skills, job_requirements.preferred_skills)
            
            # Calculate experience match
            experience_score = self._calculate_experience_match(cv.total_experience_years, job_requirements.min_experience_years)
            
            # Calculate education match
            education_score = self._calculate_education_match(cv.education, job_requirements.education_requirements)
            
            # Overall score (weighted average)
            overall_score = (skills_score * 0.5 + experience_score * 0.3 + education_score * 0.2)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(overall_score, skills_score, experience_score, education_score)
            
            # Detailed analysis
            analysis = {
                "skills_match": {
                    "score": skills_score,
                    "matched_skills": self._get_matched_skills(cv.skills, job_requirements.required_skills),
                    "missing_skills": self._get_missing_skills(cv.skills, job_requirements.required_skills)
                },
                "experience_match": {
                    "score": experience_score,
                    "candidate_years": cv.total_experience_years,
                    "required_years": job_requirements.min_experience_years
                },
                "education_match": {
                    "score": education_score,
                    "candidate_education": [edu.degree for edu in cv.education],
                    "required_education": job_requirements.education_requirements
                }
            }
            
            return CVAnalysisResponse(
                success=True,
                candidate_name=cv.name,
                overall_score=round(overall_score, 1),
                recommendation=recommendation,
                analysis=analysis
            )
            
        except Exception as e:
            logger.error(f"Error analyzing CV match: {str(e)}")
            return CVAnalysisResponse(
                success=False,
                candidate_name=cv.name,
                overall_score=0.0,
                recommendation="Error analyzing CV",
                analysis={}
            )
    
    def _calculate_skills_match(self, cv_skills: List[str], required_skills: List[str], preferred_skills: List[str]) -> float:
        """Calculate skills match score"""
        if not required_skills:
            return 100.0
        
        cv_skills_set = set(skill.lower() for skill in cv_skills)
        required_skills_set = set(skill.lower() for skill in required_skills)
        preferred_skills_set = set(skill.lower() for skill in preferred_skills)
        
        # Required skills match (80% weight)
        required_matched = len(cv_skills_set.intersection(required_skills_set))
        required_score = (required_matched / len(required_skills_set)) * 80
        
        # Preferred skills match (20% weight)
        preferred_matched = len(cv_skills_set.intersection(preferred_skills_set))
        preferred_score = (preferred_matched / len(preferred_skills_set)) * 20 if preferred_skills_set else 20
        
        return min(100.0, required_score + preferred_score)
    
    def _calculate_experience_match(self, cv_years: float, required_years: float) -> float:
        """Calculate experience match score"""
        if required_years == 0:
            return 100.0
        
        if cv_years >= required_years:
            return 100.0
        else:
            return (cv_years / required_years) * 100
    
    def _calculate_education_match(self, cv_education: List[Education], required_education: List[str]) -> float:
        """Calculate education match score"""
        if not required_education:
            return 100.0
        
        if not cv_education:
            return 0.0
        
        cv_degrees = [edu.degree.lower() for edu in cv_education]
        required_degrees = [req.lower() for req in required_education]
        
        matches = 0
        for req in required_degrees:
            for cv_deg in cv_degrees:
                if req in cv_deg or cv_deg in req:
                    matches += 1
                    break
        
        return (matches / len(required_degrees)) * 100
    
    def _get_matched_skills(self, cv_skills: List[str], required_skills: List[str]) -> List[str]:
        """Get list of matched skills"""
        cv_skills_set = set(skill.lower() for skill in cv_skills)
        required_skills_set = set(skill.lower() for skill in required_skills)
        
        matched = cv_skills_set.intersection(required_skills_set)
        return list(matched)
    
    def _get_missing_skills(self, cv_skills: List[str], required_skills: List[str]) -> List[str]:
        """Get list of missing skills"""
        cv_skills_set = set(skill.lower() for skill in cv_skills)
        required_skills_set = set(skill.lower() for skill in required_skills)
        
        missing = required_skills_set - cv_skills_set
        return list(missing)
    
    def _generate_recommendation(self, overall_score: float, skills_score: float, experience_score: float, education_score: float) -> str:
        """Generate recommendation based on scores"""
        if overall_score >= 80:
            return "Strong match - Recommend proceeding with interview"
        elif overall_score >= 60:
            return "Good match - Consider for interview with some reservations"
        elif overall_score >= 40:
            return "Partial match - May be suitable for junior roles or with training"
        else:
            return "Poor match - Not recommended for this position"