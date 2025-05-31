import requests
from typing import Dict, Optional
from bs4 import BeautifulSoup

from app.services.ai.base_ai_service import BaseAIService
from app.schemas.skill_gap import SkillGapAnalysisOutput

class SkillGapAIService(BaseAIService):
    """Service for AI-based skill gap analysis"""
    
    async def analyze_skill_gap(
        self, 
        resume_text: str, 
        job_description: str,
        job_posting_url: Optional[str] = None
    ) -> SkillGapAnalysisOutput:
        """
        Analyze the skill gap between a resume and job description
        
        Args:
            resume_text: Text content of the resume
            job_description: Text content of the job description
            job_posting_url: Optional URL of the job posting
            
        Returns:
            SkillGapAnalysisOutput containing detailed analysis
        """
        # Personal, direct system prompt
        system_prompt = """
        I want you to act as my personal career mentor and technical recruiter with 15+ years of experience. 
        You are analyzing MY resume against a specific job I'm interested in.
        
        Your goal is to provide me with extremely helpful, specific, and actionable advice that speaks directly to me.
        
        When you analyze my resume:
        - Address me directly using "you" and "your" 
        - Be brutally honest but constructive about my current standing
        - Give me specific, actionable advice I can implement immediately
        - Identify the most critical gaps I need to address first
        - Provide realistic timelines and learning paths tailored to my background
        - Recommend practical projects that directly address my skill gaps
        - Speak to me as if we're having a one-on-one career coaching session
        
        Make your analysis comprehensive, detailed, and immediately actionable. I'm counting on your expertise to guide my career development.
        """
        
        # Personal, direct user prompt
        user_prompt = f"""
        I want you to analyze my resume against this job I'm interested in and give me detailed, personal feedback:
        
        MY RESUME:
        {resume_text}
        
        JOB I'M TARGETING:
        {job_description}
        
        Please provide me with a comprehensive analysis that includes:
        
        1. Extract the exact job title and calculate how well my resume matches (0-100%)
        
        2. Analyze my matched skills - for each skill I already have:
           - Tell me what skill you found in my resume
           - Assess my proficiency level (Beginner, Intermediate, Advanced, Expert)
           - Quote specific evidence from my resume that demonstrates this skill
           - Tell me whether my experience fully meets the job requirement or only partially
        
        3. Identify my skill gaps - for each missing or weak skill:
           - Tell me exactly what skill I'm missing
           - Explain how critical this skill is (Critical, Important, Nice-to-Have)
           - Explain why I need this skill for this specific role
           - Give me a detailed, step-by-step learning path with specific resources, timeframes, and milestones
        
        4. Recommend specific projects I should build:
           - Give me 3-5 concrete project ideas that will address my skill gaps
           - For each project, tell me exactly what to build and how it helps
           - List the specific skills I'll gain from each project
           - Give me realistic time estimates and difficulty levels
           - Explain how each project directly addresses requirements in the job description
        
        5. Summarize my top 3 strengths that make me a good fit for this role
        
        6. Identify my 3 biggest gaps that could prevent me from getting this job
        
        7. Give me immediate next steps - specific actions I can take this week to improve my candidacy
        
        8. Provide a realistic timeline for when I'll be ready to confidently apply for this role
        
        9. Give me an honest overall assessment of my current fit and potential for this position
        
        Be specific, detailed, and speak directly to me. I want actionable advice that I can start implementing immediately. Don't hold back - I need your honest assessment to improve my career prospects.
        """
        
        # Make request to Groq with simplified approach
        try:
            print(f"Making Groq request for skill gap analysis...")
            print(f"Resume text length: {len(resume_text)}")
            print(f"Job description length: {len(job_description)}")
            
            result = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=SkillGapAnalysisOutput,
                temperature=0.1  # Very low temperature for consistent, focused results
            )
            
            print(f"Groq request successful, got result: {type(result)}")
            return result
        except Exception as e:
            # Log the full error details
            print(f"Skill gap analysis failed with error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            # Re-raise with more specific context
            raise Exception(f"Skill gap analysis failed: {str(e)}")
    
    async def fetch_job_description(self, url: str) -> str:
        """
        Fetch job description from a URL
        
        Args:
            url: URL of the job posting
            
        Returns:
            The extracted job description text
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find the job description section
            job_description = ""
            
            # LinkedIn
            if "linkedin.com" in url:
                job_section = soup.find("div", class_="description__text")
                if job_section:
                    job_description = job_section.get_text()
            
            # Indeed
            elif "indeed.com" in url:
                job_section = soup.find("div", id="jobDescriptionText")
                if job_section:
                    job_description = job_section.get_text()
            
            # Glassdoor
            elif "glassdoor.com" in url:
                job_section = soup.find("div", class_="jobDescriptionContent")
                if job_section:
                    job_description = job_section.get_text()
            
            # Generic fallback - try to find common job description containers
            if not job_description:
                possible_elements = [
                    soup.find("div", class_=lambda c: c and "job-description" in c.lower()),
                    soup.find("div", id=lambda i: i and "job-description" in i.lower()),
                    soup.find("section", class_=lambda c: c and ("description" in c.lower() or "requirements" in c.lower()))
                ]
                
                for element in possible_elements:
                    if element:
                        job_description = element.get_text()
                        break
            
            # Clean up the text
            job_description = self._clean_job_description(job_description)
            
            if not job_description:
                return "Could not extract job description from the provided URL."
            
            return job_description
            
        except Exception as e:
            raise Exception(f"Error fetching job description: {str(e)}")
    
    def _clean_job_description(self, text: str) -> str:
        """
        Clean up job description text
        
        Args:
            text: Raw job description text
            
        Returns:
            Cleaned job description text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        # Remove excessive newlines
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text.strip() 