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
        # Create the system prompt
        system_prompt = """
        You are a senior executive recruiter and career strategist with 15+ years of experience in technical recruiting, talent acquisition, and career development. Your specialization is in performing extremely detailed skill gap analyses for candidates.
        
        Your analytical methodology is exceptional and thorough, always considering:
        1. Explicit technical skills (languages, frameworks, tools)
        2. Implicit technical capabilities (problem-solving approach, architectural thinking)
        3. Domain knowledge and industry expertise
        4. Soft skills and leadership capabilities
        5. Cultural fit indicators
        6. Growth potential and adaptability
        
        When analyzing a resume against a job description:
        
        - Be extremely granular and specific - don't just identify "Python" as a skill, specify the level, applications, and frameworks
        - Provide detailed evidence and context from the resume that demonstrates each skill
        - For missing skills, categorize them by criticality (Critical, Important, Nice-to-Have)
        - For each missing skill, provide multiple specific, actionable learning resources with URLs, descriptions, and time commitments
        - Recommend detailed, step-by-step projects that specifically address skill gaps
        - Provide extremely specific resume improvement suggestions that would dramatically increase match rate
        - Offer direct, actionable advice framed as "you should..." rather than general observations
        
        Your analysis must be thorough yet practical - provide guidance as if the candidate is sitting across from you in a 1:1 coaching session and you're walking through exactly what they need to do to qualify for this role.
        
        Remember, the candidate is relying on your expertise to understand exactly where they stand and what specific actions they must take to succeed.
        """
        
        # Create the user prompt
        user_prompt = f"""
        Please conduct an in-depth skill gap analysis for this candidate against the specific job requirements:
        
        ## RESUME:
        {resume_text}
        
        ## JOB DESCRIPTION:
        {job_description}
        
        Your analysis must be extremely detailed and provide a comprehensive assessment with the following sections:
        
        1. JOB TITLE AND MATCH PERCENTAGE:
           - Extract the exact job title
           - Calculate a precise match percentage based on all requirements
           
        2. MATCHED SKILLS ANALYSIS:
           - For each skill, provide:
             * The exact skill name as mentioned in the job description
             * Proficiency level (Beginner, Intermediate, Advanced, Expert)
             * Match score (percentage of how well this skill matches the job requirements)
             * Direct quotes/context from the resume demonstrating this skill
             * Whether this skill meets, exceeds, or only partially meets the job requirement
           
        3. MISSING SKILLS ANALYSIS:
           - For each missing or underdeveloped skill:
             * The exact skill/requirement from the job description
             * Importance level (Critical, Important, Nice-to-Have)
             * Detailed description of what this skill entails in the context of this specific role
             * Why this skill matters for this particular position
             * 3-5 specific learning resources with direct URLs, time commitments, and difficulty levels
           
        4. PROJECT RECOMMENDATIONS:
           - 3-5 highly specific projects that:
             * Target the exact missing skills for this role
             * Include detailed step-by-step implementation plans
             * Specify technologies, tools, and methodologies to use
             * Explain how each project directly addresses requirements in the job description
             * Provide metrics to demonstrate competency upon completion
           
        5. RESUME IMPROVEMENT SUGGESTIONS:
           - Section-by-section improvement recommendations
           - Examples of stronger phrasing for existing achievements
           - Specific keywords from the job description to incorporate
           - Skills to emphasize more prominently
           * Format and presentation improvements for ATS optimization
           
        6. OVERALL ASSESSMENT:
           - Detailed evaluation of overall fit for the role
           - Specific timeframe and learning path to become fully qualified
           - Honest assessment of biggest obstacles and how to overcome them
           - Direct recommendations on whether to apply now or after addressing gaps
           - Alternative roles that might be better fits based on current qualifications
        
        Remember, be brutally honest yet constructive, extremely detailed, and provide actionable advice that the candidate can immediately implement. Focus on being comprehensive yet practical.
        """
        
        # Make request to Groq
        try:
            result = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=SkillGapAnalysisOutput,
                temperature=0.2  # Lower temperature for more focused, consistent results
            )
            return result
        except Exception as e:
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
            # This is a basic implementation and may need to be customized for different job sites
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
            
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Replace multiple newlines with a single newline
        import re
        text = re.sub(r'\n+', '\n', text)
        
        # Remove very common boilerplate text about the company
        boilerplate_phrases = [
            "Equal Opportunity Employer",
            "We are an equal opportunity employer",
            "We're an equal opportunity employer",
            "diversity and inclusion",
            "About the company",
            "About us"
        ]
        
        for phrase in boilerplate_phrases:
            if phrase.lower() in text.lower():
                # Only remove if it appears near the end of the description
                idx = text.lower().find(phrase.lower())
                if idx > 0.7 * len(text):  # If in the last 30% of the text
                    text = text[:idx]
        
        return text.strip() 