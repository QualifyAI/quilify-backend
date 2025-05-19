
from app.services.ai.base_ai_service import BaseAIService
from app.core.config import settings
from app.services.resume.models import ResumeAnalysisOutput, ImprovedResumeOutput


class ResumeAnalysisService(BaseAIService):
    """Service for analyzing and optimizing resumes"""
    
    async def analyze_resume(
        self, 
        resume_text: str, 
        job_title: str,
        industry: str
    ) -> ResumeAnalysisOutput:
        """
        Analyze a resume for ATS compatibility, content quality, and overall effectiveness
        
        Args:
            resume_text: The text content of the resume to analyze
            job_title: The target job title
            industry: The target industry
            
        Returns:
            ResumeAnalysisOutput containing detailed analysis
        """
        # Create the system prompt
        system_prompt = """
        You are an expert resume consultant with 15+ years of experience in technical recruiting, talent acquisition, and career development. 
        Your specialization is in performing extremely detailed resume analyses and providing professional improvements.
        
        You will analyze the resume in detail according to comprehensive resume criteria guidelines.
        The criteria include evaluation of:
        1. Impact - measurable achievements, action verbs, and accomplishment-focused language
        2. Brevity - conciseness, clarity, and optimal formatting
        3. Style - professionalism, readability, and modern standards
        4. Sections - structure, completeness, and organization
        5. Soft Skills - demonstration of communication, analytical, and teamwork abilities
        6. ATS Compatibility - keyword optimization and format compliance
        
        Your analysis must be extremely detailed, providing a comprehensive assessment with specific scores,
        actionable feedback, and concrete examples of improvements.
        """
        
        # Create the user prompt
        user_prompt = f"""
        Please conduct a comprehensive analysis of this resume"
        
        ## RESUME:
        {resume_text}
        
        Provide a detailed analysis including:
        
        1. Overall assessment with scores for:
           - Impact (quantifiable achievements, action verbs, tense consistency, accomplishments)
           - Brevity (bullet usage, length, filler words, page density)
           - Style (buzzwords, dates, contact details, readability, pronouns, active voice)
           - Sections (experience, education, skills, unnecessary sections)
           - Soft Skills (communication, analytical thinking, teamwork)
           - ATS Compatibility (keywords, job match, format)
        
        2. Section-by-section analysis with:
           - Score for each section
           - Specific feedback
           - Concrete improvement suggestions
           - Before/after examples
        
        3. ATS optimization:
           - Specific formatting issues
           - Keyword matching analysis
           - Recommended improvements
        
        4. Content quality:
           - Passive voice usage
           - Vague statements
           - Missing metrics
           - Action verb effectiveness
        
        5. Industry benchmark:
           - How this resume compares to industry standards
           - Competitive advantages
           - Areas needing most improvement
        
        Be extremely detailed, brutally honest yet constructive, and provide actionable recommendations that can be implemented immediately.
        """
        
        # Make request to Groq
        try:
            result = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=ResumeAnalysisOutput,
                temperature=0.3
            )
            return result
        except Exception as e:
            # Re-raise with more specific context
            raise Exception(f"Resume analysis failed: {str(e)}")
    
    async def optimize_resume(
        self, 
        resume_text: str,
        job_title: str,
        industry: str,
        analysis_result: ResumeAnalysisOutput
    ) -> ImprovedResumeOutput:
        """
        Generate an optimized version of the resume based on the analysis
        
        Args:
            resume_text: The text content of the resume to optimize
            job_title: The target job title
            industry: The target industry
            analysis_result: The analysis result from analyze_resume
            
        Returns:
            ImprovedResumeOutput containing the optimized resume and changes summary
        """
        # Create system prompt
        system_prompt = """
        You are an expert resume writer with 15+ years of experience crafting high-impact, ATS-optimized resumes
        for professionals across various industries. You specialize in transforming ordinary resumes into powerful
        marketing documents that effectively showcase a candidate's value proposition.
        
        Your task is to completely rewrite and enhance a resume based on detailed analysis findings. Your improved
        version should address all the issues identified and implement all suggested improvements.
        """
        
        # Create focused suggestions summary from analysis
        suggestions_summary = []
        
        # Add key suggestions from each category
        suggestions_summary.extend([f"IMPACT: {s}" for s in analysis_result.impact.quantifyImpact.improvementSuggestions[:3]])
        suggestions_summary.extend([f"BREVITY: {s}" for s in analysis_result.brevity.suggestions[:3]])
        suggestions_summary.extend([f"STYLE: {s}" for s in analysis_result.style.suggestions[:3]])
        suggestions_summary.extend([f"SECTIONS: {s}" for s in analysis_result.sections.suggestions[:3]])
        suggestions_summary.extend([f"SOFT SKILLS: {s}" for s in analysis_result.softSkills.suggestions[:3]])
        suggestions_summary.extend([f"ATS: {s}" for s in analysis_result.ats.suggestions[:3]])
        
        # Add section-specific suggestions
        for section_name, section in analysis_result.sectionAnalysis.items():
            section_suggestions = [f"{section_name.upper()}: {s}" for s in section.suggestions[:2]]
            suggestions_summary.extend(section_suggestions)
        
        # Create user prompt
        user_prompt = f"""
        Please create an optimized version of this resume for a {job_title} position in the {industry} industry.
        
        ## ORIGINAL RESUME:
        {resume_text}
        
        ## ANALYSIS FINDINGS:
        Key issues to address:
        {chr(10).join(f"- {s}" for s in suggestions_summary)}
        
        ## INSTRUCTIONS:
        1. Create a completely improved version of the resume in Markdown format
        2. Address ALL the issues identified in the analysis
        3. Make it visually appealing with proper formatting
        4. Include all sections (header with contact details, summary, experience, education, skills)
        5. Ensure all contact information remains the same as the original resume
        6. Enhance bullet points with metrics and accomplishments
        7. Focus on ATS optimization while maintaining readability
        8. Use strong action verbs and consistent tense
        9. Keep personal pronouns out of the resume
        10. Make the resume laser-focused for a {job_title} position
        
        The improved resume should maintain all factual information while significantly enhancing:
        - Structure and organization
        - Impact and accomplishment focus
        - ATS compatibility
        - Overall professionalism
        
        Format the output in clean, well-structured Markdown that could be easily rendered into a professional document.
        """
        
        # Make request to Groq
        try:
            result = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=ImprovedResumeOutput,
                temperature=0.4
            )
            return result
        except Exception as e:
            # Re-raise with more specific context
            raise Exception(f"Resume optimization failed: {str(e)}") 