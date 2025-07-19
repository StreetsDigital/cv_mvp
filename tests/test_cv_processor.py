import pytest
from app.services.cv_processor import CVProcessor
from app.models.cv_models import CandidateCV, JobRequirements, ContactInfo

def test_cv_processor_initialization():
    processor = CVProcessor()
    assert processor is not None
    assert hasattr(processor, 'skill_keywords')

def test_extract_cv_data():
    processor = CVProcessor()
    sample_cv = """
    John Doe
    Software Engineer
    Email: john.doe@email.com
    Phone: +1234567890
    
    Skills: Python, JavaScript, React, SQL
    
    Experience:
    Senior Developer at Tech Corp - 3 years
    Junior Developer at StartupXYZ - 2 years
    
    Education:
    Bachelor of Computer Science, University of Tech, 2018
    """
    
    cv_data = processor.extract_cv_data(sample_cv)
    
    assert isinstance(cv_data, CandidateCV)
    assert cv_data.name == "John Doe"
    assert cv_data.contact.email == "john.doe@email.com"
    assert "python" in cv_data.skills
    assert cv_data.total_experience_years > 0

def test_analyze_cv_match():
    processor = CVProcessor()
    
    # Create test CV
    cv = CandidateCV(
        name="Test Candidate",
        contact=ContactInfo(email="test@example.com"),
        skills=["python", "javascript", "react"],
        total_experience_years=3.0
    )
    
    # Create test job requirements
    job = JobRequirements(
        title="Software Engineer",
        company="Test Company",
        description="Test job description",
        required_skills=["python", "javascript"],
        min_experience_years=2.0
    )
    
    result = processor.analyze_cv_match(cv, job)
    
    assert result.success == True
    assert result.candidate_name == "Test Candidate"
    assert result.overall_score > 0
    assert "analysis" in result.dict()

def test_skills_match_calculation():
    processor = CVProcessor()
    
    cv_skills = ["python", "javascript", "react", "sql"]
    required_skills = ["python", "javascript"]
    preferred_skills = ["react"]
    
    score = processor._calculate_skills_match(cv_skills, required_skills, preferred_skills)
    
    assert score == 100.0  # Should be perfect match

def test_experience_match_calculation():
    processor = CVProcessor()
    
    # Test exact match
    score = processor._calculate_experience_match(3.0, 3.0)
    assert score == 100.0
    
    # Test exceeding requirements
    score = processor._calculate_experience_match(5.0, 3.0)
    assert score == 100.0
    
    # Test below requirements
    score = processor._calculate_experience_match(2.0, 4.0)
    assert score == 50.0