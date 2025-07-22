#!/usr/bin/env python3
"""
Test the improved scoring engine with Andrew's CV vs Mechanical Engineering job
This should show a much lower score due to domain mismatch detection
"""

import sys
import os
sys.path.append('/Users/streetsdigital/Documents/Projects/Pydantic flow - CV Screener')

from app.models.cv_models import CandidateCV, JobRequirements, ContactInfo, Experience, Education
from app.services.improved_scoring_engine import ImprovedScoringEngine

def create_andrew_cv():
    """Create Andrew's CV from the document"""
    contact = ContactInfo(
        email="andrew@streetsdigital.com",
        phone="07817 734398",
        location="4 Woodborough Hill, Peasedown St John, Bath, BA2 8LN"
    )
    
    # Extract key experiences
    experiences = [
        Experience(
            title="Head of AdOps",
            company="Forward PMX",
            duration_months=36,  # 3 years (Jan 2021 - Present in 2024)
            description="Working with Google and ASOS on programmatic advertising solutions",
            skills_used=["programmatic", "google ad manager", "campaign optimization"]
        ),
        Experience(
            title="Head of AdOps", 
            company="Crash Media Limited",
            duration_months=6,
            description="Display advertising strategy, video advertising, ad tech product management",
            skills_used=["prebid", "video advertising", "ad tech", "dmp"]
        ),
        Experience(
            title="Head of Advertising",
            company="Mixcloud Limited", 
            duration_months=15,
            description="Built smart ad refresh rules, increased programmatic revenue 300%",
            skills_used=["programmatic", "audio advertising", "ad tech", "revenue optimization"]
        ),
        Experience(
            title="Publisher Development Director",
            company="Adyoulike",
            duration_months=18,
            description="Native advertising technology, publisher development, sales management",
            skills_used=["native advertising", "publisher development", "saas sales"]
        )
    ]
    
    # Extract skills from the CV
    skills = [
        "google ad manager", "adswizz", "index exchange", "permutive", "lotame", 
        "prebid", "ssp", "facebook advertising", "google analytics", "google tag manager",
        "html", "javascript", "jira", "slack", "sql", "python", "programmatic advertising",
        "ad tech", "revenue optimization", "publisher development", "native advertising",
        "video advertising", "dmp", "campaign management", "ad operations"
    ]
    
    education = [
        Education(
            degree="Working towards data science qualification",
            institution="Unknown",
            graduation_year=None
        )
    ]
    
    return CandidateCV(
        name="Andrew Streets",
        contact=contact,
        skills=skills,
        education=education,
        experience=experiences,
        total_experience_years=10.0,
        professional_summary="Possesses a wealth of knowledge on all aspects of the online advertising ecosystem and genuine interest in ad tech/programmatic space."
    )

def create_mechanical_engineer_job():
    """Create the mechanical engineering job requirements"""
    return JobRequirements(
        title="Mechanical Design Engineer (Cryogenic Components)",
        company="Global RF Components Manufacturer",
        description="""
        Are you a Mechanical Design Engineer looking to work for a global leading manufacturer 
        who provides a stimulating technical environment with lots of opportunities to further your career?
        
        The role involves:
        - Product design using SolidWorks to create components, assemblies, engineering drawings
        - Prototyping and tooling design
        - RF or microwave connector design experience
        - Technical support for sales and manufacturing teams
        - Production engineering projects for continuous improvement
        """,
        required_skills=[
            "mechanical design", "solidworks", "cryogenic", "rf connectors", 
            "microwave connector design", "engineering drawings", "prototyping",
            "manufacturing", "production engineering", "cad", "mechanical engineering"
        ],
        preferred_skills=[
            "aerospace", "defence", "coaxial rf connectors", "cable assemblies",
            "tooling design", "materials science", "erp systems"
        ],
        min_experience_years=3.0,
        education_requirements=["mechanical engineering degree", "engineering degree"],
        salary_range_min=50000,
        salary_range_max=55000
    )

def main():
    print("🔍 Testing Improved CV Scoring Engine")
    print("=" * 50)
    
    # Create test data
    andrew_cv = create_andrew_cv()
    mech_job = create_mechanical_engineer_job()
    
    # Initialize improved scoring engine
    scoring_engine = ImprovedScoringEngine()
    
    print(f"📋 Candidate: {andrew_cv.name}")
    print(f"🎯 Job: {mech_job.title}")
    print(f"🏢 Company: {mech_job.company}")
    print()
    
    # Analyze the match
    result = scoring_engine.analyze_cv_comprehensive(andrew_cv, mech_job)
    
    print("📊 SCORING RESULTS")
    print("-" * 30)
    print(f"Overall Match Score: {result.overall_match_score}%")
    print(f"Confidence Level: {result.confidence_score}/10")
    print()
    
    print("📈 Detailed Breakdown:")
    print(f"  • Skills Match: {result.skills_match_score}%")
    print(f"  • Experience Relevance: {result.experience_relevance_score}%") 
    print(f"  • Technical Skills: {result.technical_skills_score}%")
    print()
    
    print("✅ Matched Skills:")
    for skill in result.matched_skills:
        print(f"  • {skill}")
    print()
    
    print("❌ Missing Skills:")
    for skill in result.missing_skills[:5]:  # Show first 5
        print(f"  • {skill}")
    if len(result.missing_skills) > 5:
        print(f"  ... and {len(result.missing_skills) - 5} more")
    print()
    
    print("🚩 Red Flags:")
    for flag in result.red_flags:
        print(f"  • {flag}")
    print()
    
    print("💡 Recommendation:")
    print(f"{result.recommendation}")
    print()
    
    print("🎯 Expected Result: Should be MUCH lower than 87% due to domain mismatch!")

if __name__ == "__main__":
    main()
