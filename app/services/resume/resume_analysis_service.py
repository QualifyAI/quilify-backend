from app.services.ai.base_ai_service import BaseAIService
from app.core.config import settings
from app.services.resume.models import ResumeAnalysisOutput, ImprovedResumeOutput, SimpleImprovedResumeOutput, BulletPointExample
from typing import Optional, List
from app.db.repositories.resume_analysis_repository import ResumeAnalysisRepository
from datetime import datetime


class ResumeAnalysisService(BaseAIService):
    """Service for analyzing and optimizing resumes with comprehensive scoring"""
    
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

    async def optimize_resume(
        self, 
        resume_text: str,
        job_title: str,
        industry: str,
        analysis_result: ResumeAnalysisOutput
    ) -> SimpleImprovedResumeOutput:
        """
        Generate an optimized version of the resume based on analysis results
        
        Args:
            resume_text: The text content of the resume to optimize
            job_title: The target job title
            industry: The target industry
            analysis_result: The comprehensive analysis result
            
        Returns:
            SimpleImprovedResumeOutput containing the optimized resume text
        """
        # Simple system prompt focused on text enhancement
        system_prompt = """
        You are a professional resume writer with 20+ years of experience. Your job is to enhance resumes to make them more effective for job applications.
        
        Focus on:
        - Clear, professional formatting using markdown
        - Strong action verbs and quantified achievements
        - ATS-friendly structure and keywords
        - Compelling content that highlights value
        
        Return only the enhanced resume text in markdown format along with a brief summary of changes.
        """
        
        # Extract key improvements from analysis
        missing_keywords = analysis_result.ats_compatibility.missing_keywords[:10]  # Top 10
        critical_improvements = analysis_result.critical_improvements[:5]  # Top 5
        quick_wins = analysis_result.quick_wins[:5]  # Top 5
        
        # Simple user prompt
        user_prompt = f"""
        Please enhance this resume for a {job_title} position in the {industry} industry.
        
        ORIGINAL RESUME:
        {resume_text}
        
        KEY IMPROVEMENTS NEEDED:
        - Add these missing keywords naturally: {', '.join(missing_keywords)}
        - Address these issues: {'; '.join(critical_improvements)}
        - Implement these quick wins: {'; '.join(quick_wins)}
        
        REQUIREMENTS:
        1. Use clean markdown formatting (# for name, ## for sections, ### for companies)
        2. Transform bullet points to be achievement-focused with action verbs
        3. Include relevant keywords naturally throughout
        4. Maintain professional tone and accuracy
        5. Keep the same basic structure but enhance content
        
        Provide:
        - markdown: The enhanced resume in markdown format
        - changes_summary: List of 3-5 key improvements made
        - improvement_score: Estimated score improvement (0-100)
        """
        
        # Make request to Groq for optimization
        try:
            print(f"Starting simplified resume optimization...")
            
            result = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=SimpleImprovedResumeOutput,
                temperature=0.3,
            )
            
            print(f"Resume optimization completed successfully")
            return result
        except Exception as e:
            print(f"Resume optimization failed: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Resume optimization failed: {str(e)}") 
    
    async def analyze_resume(
        self, 
        resume_text: str, 
        job_title: str,
        industry: str,
        user_id: Optional[str] = None,
        resume_id: Optional[str] = None
    ) -> ResumeAnalysisOutput:
        """
        Perform comprehensive resume analysis with detailed scoring and actionable insights
        
        Args:
            resume_text: The text content of the resume to analyze
            job_title: The target job title
            industry: The target industry
            user_id: Optional user ID for saving the result
            resume_id: Optional resume ID for saving the result
            
        Returns:
            ResumeAnalysisOutput containing comprehensive analysis with detailed scoring
        """
        # Simplified system prompt for better reliability
        system_prompt = """
        You are an expert resume consultant with 25+ years of experience. Analyze the provided resume and provide comprehensive feedback using a direct, personal approach.
        
        Your analysis must include:
        1. Overall assessment and feedback
        2. Detailed scoring across 4 main categories (ATS, Content, Format, Impact)
        3. Specific strengths and improvement areas
        4. Actionable recommendations
        5. Industry benchmarking
        
        Be thorough but ensure all required fields are populated with meaningful content.
        """
        
        # Simplified user prompt
        user_prompt = f"""
        Analyze this resume for a {job_title} position in the {industry} industry.
        
        RESUME TEXT:
        {resume_text}
        
        Provide a comprehensive analysis with:
        
        1. OVERALL ASSESSMENT (overall_score 0-100, detailed overall_feedback)
        
        2. ATS COMPATIBILITY ANALYSIS:
        - Overall ATS score and sub-scores (keyword_optimization, format_compatibility, section_structure, file_format_score)
        - List ATS strengths, issues, and recommendations
        - Identify matched_keywords and missing_keywords with keyword_density
        
        3. CONTENT QUALITY ANALYSIS:
        - Content score and sub-scores (achievement_focus, quantification, action_verbs, relevance)
        - List content strengths, weaknesses, and recommendations
        - Identify strong_bullets, weak_bullets, and quantified_achievements
        
        4. FORMAT & STRUCTURE ANALYSIS:
        - Format score and sub-scores (visual_hierarchy, consistency, readability, length_appropriateness)
        - List format strengths, issues, and recommendations
        
        5. IMPACT & EFFECTIVENESS ANALYSIS:
        - Impact score and sub-scores (first_impression, differentiation, value_proposition, memorability)
        - List impact strengths, weaknesses, and recommendations
        
        6. ACTIONABLE IMPROVEMENTS:
        - List top_strengths (5 items)
        - List critical_improvements (5 items)
        - List quick_wins (5 items)
        - Provide bullet_improvements with original/improved examples
        
        7. INDUSTRY BENCHMARKING:
        - Set industry to "{industry}"
        - Provide percentile_ranking (0-100)
        - List competitive_advantages and improvement_priorities
        - Include industry_specific_feedback
        
        8. METADATA:
        - Set target_job_title to "{job_title}"
        - Set target_industry to "{industry}"
        - Set analysis_date to "{datetime.now().strftime('%Y-%m-%d')}"
        - Estimate improvement_potential (0-100)
        
        Ensure all scores are realistic (0-100) and all lists contain meaningful, specific content.
        """
        
        # Make request to Groq with reduced complexity
        try:
            print(f"Starting simplified resume analysis for {job_title} in {industry}...")
            print(f"Resume length: {len(resume_text)} characters")
            
            result = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=ResumeAnalysisOutput,
                temperature=0.3,  # Slightly higher for more natural responses
            )
            
            print(f"Resume analysis completed successfully")
            
            # Save the analysis if user_id and resume_id are provided
            if user_id and resume_id:
                await self.save_analysis(user_id, resume_id, result)
                print(f"Analysis saved for user {user_id}")
                
            return result
        except Exception as e:
            print(f"Resume analysis failed: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Resume analysis failed: {str(e)}")
    
    