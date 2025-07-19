import logging
import asyncio
from typing import Dict, Any, List, Optional
import anthropic
from ..config import settings
from ..models.api_models import ChatMessage, ChatResponse
from ..models.cv_models import CandidateCV, JobRequirements
from ..services.cv_processor import CVProcessor
from ..services.mvp_limitations import MVPLimitationHandler

logger = logging.getLogger(__name__)

class ChatService:
    """Chat service with Claude integration for CV analysis"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.cv_processor = CVProcessor()
        self.limitation_handler = MVPLimitationHandler()
        
        # Conversation context storage (in-memory for MVP)
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        
        # System prompt for CV analysis
        self.system_prompt = """You are an expert CV Analysis Assistant for recruitment.automateengage.com. You are a senior recruitment consultant with 15+ years of experience across multiple industries.

🎯 CORE MISSION:
Help recruiters make data-driven hiring decisions through intelligent CV analysis and candidate assessment.

🧠 EXPERTISE AREAS:
1. **Technical Skills Assessment** - Evaluate programming languages, frameworks, tools, and technical depth
2. **Experience Analysis** - Assess career progression, role complexity, and industry relevance  
3. **Cultural Fit Evaluation** - Analyze soft skills, leadership potential, and team dynamics
4. **Salary & Market Analysis** - Provide insights on compensation expectations and market rates
5. **Red Flag Detection** - Identify gaps, inconsistencies, or potential concerns
6. **Growth Potential** - Assess learning ability and career trajectory

📊 ANALYSIS FRAMEWORK:
- **Technical Match (40%)**: Skills alignment with role requirements
- **Experience Quality (30%)**: Relevance, progression, and complexity of past roles
- **Cultural Fit (20%)**: Communication skills, values alignment, team collaboration
- **Growth Potential (10%)**: Learning ability, adaptability, and future contribution

💡 RESPONSE STYLE:
- Be specific and actionable (provide exact recommendations)
- Use data and evidence from the CV to support conclusions
- Offer both positive aspects and areas for improvement
- Suggest specific interview questions to explore further
- Provide market insights when relevant

🚨 RED FLAGS TO WATCH FOR:
- Frequent job hopping without clear progression
- Gaps in employment without explanation
- Skills misalignment with claimed experience level
- Poor communication in CV presentation
- Outdated technology stack for senior roles

Always provide a confidence score (1-10) for your assessment and explain your reasoning."""

    async def process_message(self, message: ChatMessage, session_id: str) -> ChatResponse:
        """Process a chat message and return response"""
        try:
            # Initialize conversation if new
            if session_id not in self.conversations:
                self.conversations[session_id] = []
            
            # Add user message to conversation
            self.conversations[session_id].append({
                "role": "user",
                "content": message.content
            })
            
            # Handle different message types
            if message.message_type == "file":
                return await self._handle_file_message(message, session_id)
            elif message.message_type == "text":
                return await self._handle_text_message(message, session_id)
            else:
                return ChatResponse(
                    content="Sorry, I can only process text and file messages.",
                    message_type="system"
                )
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return ChatResponse(
                content="I encountered an error processing your message. Please try again.",
                message_type="system"
            )
    
    async def _handle_file_message(self, message: ChatMessage, session_id: str) -> ChatResponse:
        """Handle file upload messages"""
        if not message.file_name or not message.content:
            return ChatResponse(
                content="I didn't receive the file content. Please try uploading again.",
                message_type="system"
            )
        
        # Extract CV data
        cv_data = self.cv_processor.extract_cv_data(message.content)
        
        # Store CV data in conversation context
        self.conversations[session_id].append({
            "role": "assistant",
            "content": f"CV uploaded and analyzed for {cv_data.name}",
            "cv_data": cv_data.dict()
        })
        
        # Generate response
        response_content = f"""📄 **CV Analysis Complete**

**Candidate:** {cv_data.name}
**Experience:** {cv_data.total_experience_years} years
**Skills:** {', '.join(cv_data.skills[:10])}{'...' if len(cv_data.skills) > 10 else ''}

I've successfully analyzed the CV. You can now:
1. Upload a job description to get a match score
2. Ask specific questions about this candidate
3. Request detailed analysis of their experience

What would you like to do next?"""

        return ChatResponse(
            content=response_content,
            message_type="text",
            metadata={"cv_data": cv_data.dict()}
        )
    
    async def _handle_text_message(self, message: ChatMessage, session_id: str) -> ChatResponse:
        """Handle text messages"""
        content = message.content.lower().strip()
        
        # Handle common commands
        if content in ["help", "/help"]:
            return self._get_help_response()
        
        if content in ["clear", "/clear"]:
            self.conversations[session_id] = []
            return ChatResponse(
                content="Conversation cleared. How can I help you with CV analysis?",
                message_type="system"
            )
        
        # Check for premium feature requests
        if any(keyword in content for keyword in ["email", "send email", "linkedin", "connect"]):
            limitation_data = self.limitation_handler.get_limitation_message("email_integration")
            return ChatResponse(
                content=limitation_data["content"],
                message_type="system",
                metadata=limitation_data
            )
        
        # Get Claude response
        return await self._get_claude_response(message.content, session_id)
    
    async def _get_claude_response(self, user_message: str, session_id: str) -> ChatResponse:
        """Get response from Claude"""
        try:
            # Prepare conversation history
            messages = []
            for msg in self.conversations[session_id][-10:]:  # Last 10 messages for context
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Call Claude
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=self.system_prompt,
                messages=messages
            )
            
            claude_response = response.content[0].text
            
            # Add assistant response to conversation
            self.conversations[session_id].append({
                "role": "assistant",
                "content": claude_response
            })
            
            return ChatResponse(
                content=claude_response,
                message_type="text"
            )
            
        except Exception as e:
            logger.error(f"Error getting Claude response: {str(e)}")
            return ChatResponse(
                content="I'm having trouble connecting to my analysis engine. Please try again in a moment.",
                message_type="system"
            )
    
    def _get_help_response(self) -> ChatResponse:
        """Return help information"""
        help_content = """🤖 **CV Analysis Assistant Help**

**How to use:**
1. **Upload a CV** - Drag & drop or click to upload PDF, DOCX, or TXT files
2. **Ask questions** - Ask about candidate skills, experience, or qualifications
3. **Job matching** - Upload or paste job descriptions for match analysis

**Sample questions:**
• "Analyze this candidate's technical skills"
• "How many years of Python experience do they have?"
• "Would this candidate be good for a senior developer role?"
• "What are their strongest qualifications?"

**Commands:**
• `help` - Show this help
• `clear` - Clear conversation

**File formats supported:** PDF, DOCX, TXT (max 5MB)

Ready to analyze CVs! Upload a file or ask a question to get started."""

        return ChatResponse(
            content=help_content,
            message_type="text"
        )
    
    async def analyze_cv_with_job(self, cv_text: str, job_description: str, session_id: str) -> ChatResponse:
        """Analyze CV against job requirements"""
        try:
            # Extract CV data
            cv_data = self.cv_processor.extract_cv_data(cv_text)
            
            # Parse job requirements (simplified for MVP)
            job_requirements = self._parse_job_description(job_description)
            
            # Perform analysis
            analysis_result = self.cv_processor.analyze_cv_match(cv_data, job_requirements)
            
            if not analysis_result.success:
                return ChatResponse(
                    content="Failed to analyze CV match. Please try again.",
                    message_type="system"
                )
            
            # Format response
            score_emoji = "🟢" if analysis_result.overall_score >= 70 else "🟡" if analysis_result.overall_score >= 50 else "🔴"
            
            response_content = f"""📊 **CV Match Analysis Complete**

{score_emoji} **Overall Score: {analysis_result.overall_score}/100**

**Candidate:** {analysis_result.candidate_name}
**Recommendation:** {analysis_result.recommendation}

**Detailed Breakdown:**
• **Skills Match:** {analysis_result.analysis['skills_match']['score']:.1f}/100
• **Experience Match:** {analysis_result.analysis['experience_match']['score']:.1f}/100
• **Education Match:** {analysis_result.analysis['education_match']['score']:.1f}/100

**Matched Skills:** {', '.join(analysis_result.analysis['skills_match']['matched_skills'])}
**Missing Skills:** {', '.join(analysis_result.analysis['skills_match']['missing_skills'])}

Would you like me to provide more detailed analysis or suggest next steps?"""
            
            return ChatResponse(
                content=response_content,
                message_type="text",
                metadata={"analysis_result": analysis_result.dict()}
            )
            
        except Exception as e:
            logger.error(f"Error analyzing CV with job: {str(e)}")
            return ChatResponse(
                content="Error performing CV analysis. Please try again.",
                message_type="system"
            )
    
    def _parse_job_description(self, job_description: str) -> JobRequirements:
        """Parse job description into structured requirements (simplified)"""
        # This is a simplified parser for MVP
        # In production, this would use more sophisticated NLP
        
        lines = job_description.lower()
        
        # Extract basic info
        title = "Software Engineer"  # Default
        company = "Company"  # Default
        
        # Simple skill extraction
        common_skills = ['python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker']
        required_skills = [skill for skill in common_skills if skill in lines]
        
        # Simple experience extraction
        min_experience = 0
        if "senior" in lines:
            min_experience = 5
        elif "mid-level" in lines or "intermediate" in lines:
            min_experience = 3
        elif "junior" in lines:
            min_experience = 1
        
        return JobRequirements(
            title=title,
            company=company,
            description=job_description,
            required_skills=required_skills,
            preferred_skills=[],
            min_experience_years=min_experience,
            education_requirements=[]
        )