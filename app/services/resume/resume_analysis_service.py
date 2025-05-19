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
        # Create system prompt with emphasis on beautiful formatting
        system_prompt = """
        You are an elite resume designer with 20+ years of experience crafting visually stunning, ATS-optimized resumes 
        for top executives and professionals. You've helped thousands of clients land jobs at Fortune 500 companies.
        
        Your task is to completely transform this resume into a masterpiece that combines:
        1. Compelling, achievement-oriented content
        2. Clean, modern design with perfect spacing and alignment
        3. Strategic keyword placement for ATS optimization
        4. Visual hierarchy that guides the reader's eye
        5. Perfect balance of white space and content density
        
        The output should be in Markdown format, but you MUST use advanced Markdown formatting to create 
        a resume that looks professionally designed:
        
        - Use headings (# ## ###) strategically for section titles and name
        - Use horizontal rules (---) to create visual separation
        - Use bold and italics to emphasize key information
        - Use tables for clean alignment of dates and locations
        - Use bullet points with proper indentation hierarchies
        - Add subtle Unicode symbols (like → ● ○ ■ □) where appropriate
        - Use line breaks strategically to create proper spacing
        - Create visual distinction between sections
        
        Your goal is to make this the most impressive resume the candidate has ever had - one that not only passes ATS systems
        but also wows hiring managers and recruiters with its professional look and compelling content.
        """
        
        # Extract key recommendations from the analysis
        content_recommendations = analysis_result.content.recommendations
        format_recommendations = analysis_result.formatting.recommendations
        impact_recommendations = analysis_result.impact.recommendations 
        ats_recommendations = analysis_result.ats.recommendations
        weaknesses = analysis_result.topWeaknesses
        strengths = analysis_result.topStrengths
        
        # Create a consolidated list of improvements to make
        improvement_points = content_recommendations + format_recommendations + impact_recommendations + ats_recommendations + weaknesses
        
        # Create bullet point example string
        bullet_point_examples = ""
        for example in analysis_result.bulletPointExamples:
            bullet_point_examples += f"- Before: {example.before}\n  After: {example.after}\n"
        
        # Create user prompt with detailed guidance on resume structure
        user_prompt = f"""
        Transform this resume into a professional, visually appealing document for a {job_title} position in the {industry} industry.
        
        ## ORIGINAL RESUME:
        {resume_text}
        
        ## ANALYSIS FINDINGS:
        Key issues to address:
        {chr(10).join(f"- {point}" for point in improvement_points)}
        
        Key strengths to highlight:
        {chr(10).join(f"- {strength}" for strength in strengths)}
        
        ## BULLET POINT IMPROVEMENTS:
        {bullet_point_examples}
        
        ## KEYWORD OPPORTUNITIES:
        Missing keywords to add: {', '.join(analysis_result.keywordAnalysis.missing)}
        
        ## DESIGN REQUIREMENTS:
        Create a clean, modern resume with the following sections:
        
        1. HEADER
           - Name (prominently displayed)
           - Contact information (phone, email, LinkedIn, location)
           - Optional: Professional title aligned with target job
        
        2. PROFESSIONAL SUMMARY
           - Compelling 3-4 line summary highlighting key qualifications
           - Include top keywords from the job title and industry
           - Focus on unique value proposition and career highlights
        
        3. SKILLS SECTION
           - Organized in categories (Technical, Professional, etc.)
           - Prioritize keywords relevant to the job
           - Include all matched keywords: {', '.join(analysis_result.keywordAnalysis.matched)}
           - Add missing keywords: {', '.join(analysis_result.keywordAnalysis.missing)}
        
        4. PROFESSIONAL EXPERIENCE
           - Company name, location, job title with clear formatting
           - Dates formatted consistently (MM/YYYY or YYYY)
           - Accomplishment-focused bullet points with metrics
           - Start each bullet with strong action verbs
           - Include 3-5 bullets per position, focused on achievements
        
        5. EDUCATION
           - Degree, institution, graduation date
           - Relevant coursework or achievements if applicable
        
        6. ADDITIONAL SECTIONS (if relevant)
           - Certifications
           - Projects
           - Volunteer work
           - Publications/Patents
        
        ## MARKDOWN FORMATTING GUIDELINES:
        - Use level 1 heading (#) for name
        - Use level 2 headings (##) for main sections
        - Use level 3 headings (###) for company names or degrees
        - Use **bold** for job titles and degrees
        - Use *italics* for dates and locations
        - Use horizontal rules (---) to separate major sections
        - Use bullet points with consistent indentation
        - Use columns for skills section (using HTML table syntax if needed)
        - Ensure proper spacing between sections
        - Use Unicode symbols (→, •, ◦, etc.) for visual enhancement
        
        ## CONTENT REQUIREMENTS:
        - Transform all weak bullet points into achievement-focused statements
        - Quantify achievements with metrics where possible (%, $, time saved)
        - Use strong action verbs at the start of each bullet
        - Eliminate first-person pronouns (I, me, my)
        - Use present tense for current positions, past tense for previous roles
        - Include relevant keywords naturally throughout
        - Ensure all information from original resume is preserved with proper context
        
        ## RESPONSE REQUIREMENTS:
        In addition to providing the optimized resume in markdown format, please include:
        
        1. changesSummary: List at least 5 major changes you made to improve the resume
        
        2. improvementScore: Estimate the percentage improvement (0-100) this resume represents compared to the original
        
        3. sectionImprovements: For each section (Summary, Experience, Skills, Education, etc.), list specific improvements made
        
        4. keywordsAdded: List all the keywords you added to the resume that weren't in the original
        
        5. formattingImprovements: List all formatting improvements made to enhance visual appeal and readability
        
        6. contentImprovements: List all content improvements made to strengthen impact and effectiveness
        
        Create the most impressive, professional-looking resume possible that would pass any ATS system and impress any hiring manager.
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