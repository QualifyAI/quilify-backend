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
        # Simplified system prompt focused on actionable insights
        system_prompt = """
        You are an expert technical recruiter and career mentor with 15+ years of experience. 
        Your goal is to provide extremely helpful, specific, and actionable skill gap analysis.
        
        Focus on:
        - Being brutally honest but constructive
        - Providing specific, actionable advice
        - Identifying the most critical gaps first
        - Giving realistic timelines and learning paths
        - Recommending practical projects that directly address gaps
        
        Keep your analysis practical and immediately actionable.
        """
        
        # Simplified user prompt with clear structure
        user_prompt = f"""
        Analyze this resume against the job requirements and provide specific, actionable insights:
        
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide your analysis in this exact format:
        
        1. Extract the job title from the job description
        2. Calculate match percentage (0-100) based on how well the resume fits
        3. List matched skills with evidence from resume
        4. List missing critical skills with specific learning paths
        5. Recommend 3-5 specific projects to build missing skills
        6. Identify top 3 strengths and top 3 gaps
        7. Give immediate next steps and realistic timeline
        8. Provide honest overall assessment
        
        Be specific, actionable, and focus on what the candidate can do immediately to improve their chances.
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