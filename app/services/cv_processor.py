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
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 'laravel', 'rails', 'nextjs', 'nuxt'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite', 'cassandra', 'dynamodb', 'neo4j'],
            'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'github actions', 'gitlab ci'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'figma', 'adobe', 'photoshop', 'sketch', 'linux', 'windows', 'macos'],
            'data_science': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'tableau', 'power bi', 'excel', 'spark'],
            'mobile': ['react native', 'flutter', 'swift', 'kotlin', 'ionic', 'xamarin', 'android', 'ios'],
            'testing': ['jest', 'pytest', 'selenium', 'cypress', 'junit', 'mocha', 'testing', 'unit test', 'integration test'],
            'security': ['cybersecurity', 'penetration testing', 'ethical hacking', 'security', 'ssl', 'oauth', 'jwt'],
            'management': ['project management', 'agile', 'scrum', 'kanban', 'team lead', 'leadership', 'management']
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
        
        # Enhanced name patterns with more variations
        name_patterns = [
            r'(?:Name|Full Name|Candidate Name)[:\s]+([A-Za-z\s\-\'\.]+)',
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*$',  # 2-4 names at start of line
            r'([A-Z][A-Z\s]+[A-Z])',  # ALL CAPS names
            r'([A-Z][a-z]+\s+[A-Z]\.?\s+[A-Z][a-z]+)',  # First Middle Last
            r'([A-Z][a-z]+(?:\s+[a-z]+)?\s+[A-Z][a-z]+)',  # First von Last
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                name = match.group(1).strip()
                # Validate name (not too long, contains alphabetic chars)
                if 2 <= len(name.split()) <= 5 and any(c.isalpha() for c in name):
                    return self._clean_name(name)
        
        # Fallback: analyze first few lines more intelligently
        for line in lines[:8]:
            line = line.strip()
            # Skip empty lines, emails, phones, addresses
            if (line and not re.search(r'[@\+\d]', line) and 
                len(line.split()) <= 4 and 
                all(word.replace('-', '').replace("'", "").replace('.', '').isalpha() for word in line.split())):
                if len(line) > 4:  # Avoid single letters or very short strings
                    return self._clean_name(line)
        
        return "Unknown Candidate"
    
    def _clean_name(self, name: str) -> str:
        """Clean and format extracted name"""
        # Remove extra whitespace and common prefixes/suffixes
        name = re.sub(r'\s+', ' ', name.strip())
        name = re.sub(r'^(Mr|Ms|Mrs|Dr|Prof)\.?\s+', '', name, flags=re.IGNORECASE)
        
        # Title case
        words = []
        for word in name.split():
            if word.upper() in ['II', 'III', 'IV', 'JR', 'SR']:
                words.append(word.upper())
            else:
                words.append(word.capitalize())
        
        return ' '.join(words)
    
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
        """Extract work experience with comprehensive date parsing"""
        experience_list = []
        
        # Look for experience section first
        experience_sections = [
            r'(?:experience|employment|work history|professional experience|career)[:\s]+(.*?)(?=\n\s*(?:education|skills|projects|qualifications|references)|$)',
            r'(?:work experience|professional background)[:\s]+(.*?)(?=\n\s*(?:education|skills|projects|qualifications|references)|$)'
        ]
        
        experience_text = ""
        for pattern in experience_sections:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                experience_text = match.group(1)
                break
        
        if not experience_text:
            # Fallback: look for common job patterns throughout the text
            experience_text = text
        
        # Enhanced patterns for different CV formats
        job_patterns = [
            # Standard format: Title, Company, Dates
            r'([A-Za-z\s&,.-]{10,60})\n.*?([A-Za-z\s&,.-]{2,40})\n.*?(\d{1,2}\/\d{4}|[A-Za-z]{3,9}\s+\d{4}).*?(?:[-–]|to|present|\n).*?(\d{1,2}\/\d{4}|[A-Za-z]{3,9}\s+\d{4}|present)',
            # Inline format: Title at Company (Date - Date)
            r'([A-Za-z\s&,.-]{5,50})\s+(?:at|@|\|)\s+([A-Za-z\s&,.-]{2,40}).*?(\d{1,2}\/\d{4}|[A-Za-z]{3,9}\s+\d{4}).*?[-–].*?(\d{1,2}\/\d{4}|[A-Za-z]{3,9}\s+\d{4}|present)',
            # Years only format: Title at Company (2020-2023)
            r'([A-Za-z\s&,.-]{5,50})\s+(?:at|@|\|)\s+([A-Za-z\s&,.-]{2,40}).*?(\d{4}).*?[-–].*?(\d{4}|present)',
            # Duration format: Title at Company - 2 years 3 months
            r'([A-Za-z\s&,.-]{5,50})\s+(?:at|@|\|)\s+([A-Za-z\s&,.-]{2,40}).*?(\d{1,2})\s*(?:years?|yrs?)(?:\s*(\d{1,2})\s*(?:months?|mos?))?'
        ]
        
        for pattern in job_patterns:
            matches = re.finditer(pattern, experience_text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                title = self._clean_text(match.group(1))
                company = self._clean_text(match.group(2))
                
                # Skip if title or company seem invalid
                if not self._is_valid_job_info(title, company):
                    continue
                
                # Calculate duration based on pattern type
                duration_months = self._calculate_job_duration(match.groups())
                
                if title and company and duration_months > 0:
                    experience_list.append(Experience(
                        title=title,
                        company=company,
                        duration_months=duration_months,
                        description=None,
                        skills_used=[]
                    ))
        
        # If no experiences found, try simple fallback
        if not experience_list:
            experience_list = self._fallback_experience_extraction(text)
        
        return experience_list
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        # Remove extra whitespace and common prefixes
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'^[-•·\s]+', '', text)
        return text
    
    def _is_valid_job_info(self, title: str, company: str) -> bool:
        """Validate if extracted job info seems legitimate"""
        # Skip if too short or contains invalid patterns
        invalid_patterns = [
            r'^\d+$',  # Just numbers
            r'^[^a-zA-Z]*$',  # No letters
            r'email|phone|address|linkedin',  # Contact info
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, title.lower()) or re.search(pattern, company.lower()):
                return False
        
        return len(title) >= 3 and len(company) >= 2
    
    def _calculate_job_duration(self, groups: tuple) -> int:
        """Calculate job duration in months from regex groups"""
        try:
            if len(groups) >= 4:
                start_date = groups[2]
                end_date = groups[3]
                
                # Handle "present" or current job
                if 'present' in end_date.lower() or 'current' in end_date.lower():
                    import datetime
                    current_year = datetime.datetime.now().year
                    end_date = str(current_year)
                
                # Extract years from dates
                start_year = self._extract_year_from_date(start_date)
                end_year = self._extract_year_from_date(end_date)
                
                if start_year and end_year:
                    years_diff = end_year - start_year
                    return max(1, years_diff * 12)  # Convert to months, minimum 1 month
                
            # Handle direct year/month format (last group pattern)
            elif len(groups) >= 3 and groups[2].isdigit():
                years = int(groups[2])
                months = 0
                if len(groups) >= 4 and groups[3] and groups[3].isdigit():
                    months = int(groups[3])
                return years * 12 + months
                
        except Exception as e:
            logger.debug(f"Error calculating duration: {e}")
        
        return 12  # Default to 1 year if calculation fails
    
    def _extract_year_from_date(self, date_str: str) -> Optional[int]:
        """Extract year from various date formats"""
        if not date_str:
            return None
        
        # Look for 4-digit year
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            year = int(year_match.group())
            if 1980 <= year <= 2030:  # Reasonable range
                return year
        
        return None
    
    def _fallback_experience_extraction(self, text: str) -> List[Experience]:
        """Fallback method for experience extraction"""
        experience_list = []
        
        # Look for any mention of years of experience
        total_exp_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(?:experience|exp).*?(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*(?:experience|exp)'
        ]
        
        for pattern in total_exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                years = int(match.group(1))
                experience_list.append(Experience(
                    title="Professional Experience",
                    company="Various",
                    duration_months=years * 12,
                    description=f"Total {years} years of professional experience mentioned",
                    skills_used=[]
                ))
                break
        
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
            
            # Calculate additional factors
            career_progression_score = self._calculate_career_progression(cv.experience)
            skills_depth_score = self._calculate_skills_depth(cv.skills, cv.total_experience_years)
            
            # Overall score (weighted average with new factors)
            overall_score = (
                skills_score * 0.35 + 
                experience_score * 0.25 + 
                education_score * 0.15 +
                career_progression_score * 0.15 +
                skills_depth_score * 0.10
            )
            
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
    
    def _calculate_career_progression(self, experience: List[Experience]) -> float:
        """Calculate career progression score based on role advancement"""
        if len(experience) < 2:
            return 50.0  # Neutral score for limited experience
        
        # Look for progression indicators
        progression_indicators = ['senior', 'lead', 'manager', 'director', 'principal', 'architect', 'head']
        
        score = 50.0  # Base score
        
        for i, exp in enumerate(experience):
            title_lower = exp.title.lower()
            
            # Check for upward progression in titles
            for indicator in progression_indicators:
                if indicator in title_lower:
                    score += 10.0  # Boost for leadership roles
                    break
            
            # Check for increasing responsibility (longer tenures at later roles)
            if i > 0 and exp.duration_months > experience[i-1].duration_months:
                score += 5.0
        
        return min(100.0, score)
    
    def _calculate_skills_depth(self, skills: List[str], years_experience: float) -> float:
        """Calculate skills depth vs experience ratio"""
        if years_experience == 0:
            return 0.0
        
        # Expected skills per year of experience
        expected_skills_ratio = 3.0  # 3 skills per year is reasonable
        actual_ratio = len(skills) / years_experience
        
        # Score based on how close to expected ratio
        if actual_ratio >= expected_skills_ratio:
            return 100.0
        else:
            return (actual_ratio / expected_skills_ratio) * 100.0

    def _generate_recommendation(self, overall_score: float, skills_score: float, experience_score: float, education_score: float) -> str:
        """Generate recommendation based on scores"""
        if overall_score >= 85:
            return "🟢 STRONG MATCH - Highly recommend proceeding with immediate interview. Excellent candidate."
        elif overall_score >= 75:
            return "🟢 GOOD MATCH - Recommend interview. Strong candidate with minor gaps."
        elif overall_score >= 65:
            return "🟡 MODERATE MATCH - Consider for interview. Some concerns to address."
        elif overall_score >= 50:
            return "🟡 PARTIAL MATCH - May suit with training or junior-level adjustment."
        elif overall_score >= 35:
            return "🔴 WEAK MATCH - Significant gaps. Consider only if desperate."
        else:
            return "🔴 POOR MATCH - Not recommended. Major misalignment with requirements."