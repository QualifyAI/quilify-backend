from app.services.ai.base_ai_service import BaseAIService
from app.core.config import settings
from app.services.resume.models import ResumeAnalysisOutput, ImprovedResumeOutput, BulletPointExample, ResumeSection, KeywordAnalysis
from typing import Optional, List
from app.db.repositories.resume_analysis_repository import ResumeAnalysisRepository


class ResumeAnalysisService(BaseAIService):
    """Service for analyzing and optimizing resumes"""
    
    def __init__(self):
        super().__init__()
        self.repository = ResumeAnalysisRepository()
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[ResumeAnalysisOutput]:
        """
        Retrieve a previously saved resume analysis by ID
        
        Args:
            analysis_id: ID of the analysis to retrieve
            
        Returns:
            ResumeAnalysisOutput if found, None otherwise
        """
        return await self.repository.get_analysis_by_id(analysis_id)
    
    async def save_analysis(self, user_id: str, resume_id: str, analysis_result: ResumeAnalysisOutput) -> str:
        """
        Save an analysis result to the database
        
        Args:
            user_id: ID of the user who owns the analysis
            resume_id: ID of the resume that was analyzed
            analysis_result: The analysis result to save
            
        Returns:
            ID of the saved analysis
        """
        analysis_data = analysis_result.model_dump()
        return await self.repository.save_analysis(user_id, resume_id, analysis_data)
    
    async def analyze_resume(
        self, 
        resume_text: str, 
        job_title: str,
        industry: str,
        user_id: Optional[str] = None,
        resume_id: Optional[str] = None
    ) -> ResumeAnalysisOutput:
        """
        Analyze a resume for ATS compatibility, content quality, and overall effectiveness
        
        Args:
            resume_text: The text content of the resume to analyze
            job_title: The target job title
            industry: The target industry
            user_id: Optional user ID for saving the result
            resume_id: Optional resume ID for saving the result
            
        Returns:
            ResumeAnalysisOutput containing detailed analysis
        """
        # Create the system prompt - simpler and more direct
        system_prompt = """
        You are an elite resume consultant with 20+ years of experience helping candidates land jobs at top companies.
        
        You will analyze the provided resume thoroughly and provide detailed, specific, and actionable feedback.
        Write as if you are speaking directly to the candidate in first person.
        
        Your analysis MUST include:
        
        1. SPECIFIC examples from the resume - never be generic
        2. CONCRETE, detailed recommendations that the candidate can immediately implement
        3. HONEST but constructive criticism - point out real flaws directly
        4. Direct comparisons to industry standards based on your expertise
        
        CRITICAL REQUIREMENTS:
        - For ALL list fields, provide AT LEAST 3-5 specific items
        - Be extremely detailed and thorough
        - Use first-person language throughout (e.g., "Your resume shows..." or "I noticed...")
        - For each criticism, provide a specific example of how to improve it
        - Include real examples from the resume in your analysis
        - For bullet point examples, take ACTUAL bullets from their resume and show improved versions
        
        The output will follow a predefined schema, but make your analysis extremely detailed and personalized.
        """
        
        # Create the user prompt - more concise and focused
        user_prompt = f"""
        Please analyze this resume for a {job_title} position in the {industry} industry.
        
        RESUME TEXT:
        {resume_text}
        
        Provide comprehensive feedback covering:
        
        1. OVERALL ASSESSMENT - Give a detailed overall assessment (at least 3 paragraphs)
        
        2. CONTENT ANALYSIS
           - What specific strengths does the content have? (at least 3)
           - What specific weaknesses in the content need improvement? (at least 3)
           - What specific recommendations do you have to improve the content? (at least 3)
           - Score the content quality from 0-100
        
        3. FORMATTING ANALYSIS
           - What specific strengths does the formatting have? (at least 3)
           - What specific weaknesses in formatting need improvement? (at least 3)
           - What specific recommendations do you have to improve formatting? (at least 3)
           - Score the formatting from 0-100
        
        4. IMPACT ANALYSIS
           - What makes this resume impactful? (at least 3 specific strengths)
           - What reduces the impact of this resume? (at least 3 specific weaknesses)
           - How can the candidate make the resume more impactful? (at least 3 specific recommendations)
           - Score the impact from 0-100
        
        5. ATS COMPATIBILITY ANALYSIS
           - What makes this resume ATS-friendly? (at least 3 specific strengths)
           - What ATS issues does this resume have? (at least 3 specific weaknesses)
           - How can the candidate improve ATS compatibility? (at least 3 specific recommendations)
           - Score the ATS compatibility from 0-100
        
        6. TOP STRENGTHS & WEAKNESSES
           - List at least 5 specific top strengths from the entire resume
           - List at least 5 specific top weaknesses from the entire resume
        
        7. BULLET POINT IMPROVEMENTS
           - Take at least 3 actual bullet points from the resume
           - Provide improved versions that are more impactful and ATS-friendly
        
        8. KEYWORD ANALYSIS
           - List at least 5 industry keywords already present in the resume
           - List at least 5 important keywords missing from the resume
           - Provide at least 3 specific recommendations for incorporating missing keywords
        
        9. INDUSTRY COMPARISON
           - Provide a detailed comparison (at least 2 paragraphs) of this resume to industry standards
           - Be specific about how this resume compares to others you've seen for similar roles
        
        10. OVERALL SCORE
            - Provide an overall score from 0-100
        
        Make this the most detailed, thorough, and helpful resume analysis possible.
        """
        
        # Make request to Groq
        try:
            result = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=ResumeAnalysisOutput,
                temperature=0.2
            )
            
            # Save the analysis if user_id and resume_id are provided
            if user_id and resume_id:
                await self.save_analysis(user_id, resume_id, result)
                
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
        
        # Extract key recommendations from the analysis
        content_recommendations = analysis_result.content.recommendations
        format_recommendations = analysis_result.formatting.recommendations
        impact_recommendations = analysis_result.impact.recommendations 
        ats_recommendations = analysis_result.ats.recommendations
        weaknesses = analysis_result.topWeaknesses
        
        # Create a consolidated list of improvements to make
        improvement_points = content_recommendations + format_recommendations + impact_recommendations + ats_recommendations + weaknesses
        
        # Create bullet point example string
        bullet_point_examples = ""
        for example in analysis_result.bulletPointExamples:
            bullet_point_examples += f"- Before: {example.before}\n  After: {example.after}\n"
        
        # Create user prompt
        user_prompt = f"""
        Please create an optimized version of this resume for a {job_title} position in the {industry} industry.
        
        ## ORIGINAL RESUME:
        {resume_text}
        
        ## ANALYSIS FINDINGS:
        Key issues to address:
        {chr(10).join(f"- {point}" for point in improvement_points)}
        
        ## BULLET POINT IMPROVEMENTS:
        {bullet_point_examples}
        
        ## KEYWORD OPPORTUNITIES:
        Missing keywords to add: {', '.join(analysis_result.keywordAnalysis.missing)}
        
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
                temperature=0.3
            )
            return result
        except Exception as e:
            # Re-raise with more specific context
            raise Exception(f"Resume optimization failed: {str(e)}") 