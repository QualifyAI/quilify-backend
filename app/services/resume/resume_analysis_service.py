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
        I want you to act as my personal resume consultant with 20+ years of experience helping people like me land jobs at top companies.
        You are analyzing MY resume and I need your honest, detailed feedback.
        
        Your goal is to provide me with extremely helpful, specific, and actionable advice that speaks directly to me.
        
        When you analyze my resume:
        - Address me directly using "you" and "your" throughout your analysis
        - Be brutally honest but constructive about my current resume
        - Give me specific, actionable advice I can implement immediately
        - Point out real flaws directly and tell me exactly how to fix them
        - Use specific examples from MY resume in your feedback
        - Speak to me as if we're having a one-on-one consultation session
        
        Your analysis MUST include:
        1. SPECIFIC examples from my resume - never be generic
        2. CONCRETE, detailed recommendations that I can immediately implement
        3. HONEST but constructive criticism - point out real flaws directly
        4. Direct comparisons to industry standards based on your expertise
        
        CRITICAL REQUIREMENTS:
        - For ALL list fields, provide AT LEAST 3-5 specific items
        - Be extremely detailed and thorough
        - Use first-person language throughout (e.g., "Your resume shows..." or "I noticed...")
        - For each criticism, provide a specific example of how to improve it
        - Include real examples from my resume in your analysis
        - For bullet point examples, take ACTUAL bullets from my resume and show improved versions
        
        Make your analysis comprehensive, detailed, and immediately actionable. I'm counting on your expertise to help me improve my resume.
        """
        
        # Create the user prompt - more concise and focused
        user_prompt = f"""
        I want you to analyze MY resume for a {job_title} position in the {industry} industry and give me detailed, personal feedback.
        
        MY RESUME TEXT:
        {resume_text}
        
        Please provide me with comprehensive feedback covering:
        
        1. OVERALL ASSESSMENT - Give me a detailed overall assessment of my resume (at least 3 paragraphs)
        
        2. CONTENT ANALYSIS
           - What specific strengths does my content have? (at least 3)
           - What specific weaknesses in my content need improvement? (at least 3)
           - What specific recommendations do you have to improve my content? (at least 3)
           - Score my content quality from 0-100
        
        3. FORMATTING ANALYSIS
           - What specific strengths does my formatting have? (at least 3)
           - What specific weaknesses in my formatting need improvement? (at least 3)
           - What specific recommendations do you have to improve my formatting? (at least 3)
           - Score my formatting from 0-100
        
        4. IMPACT ANALYSIS
           - What makes my resume impactful? (at least 3 specific strengths)
           - What reduces the impact of my resume? (at least 3 specific weaknesses)
           - How can I make my resume more impactful? (at least 3 specific recommendations)
           - Score my impact from 0-100
        
        5. ATS COMPATIBILITY ANALYSIS
           - What makes my resume ATS-friendly? (at least 3 specific strengths)
           - What ATS issues does my resume have? (at least 3 specific weaknesses)
           - How can I improve my ATS compatibility? (at least 3 specific recommendations)
           - Score my ATS compatibility from 0-100
        
        6. TOP STRENGTHS & WEAKNESSES
           - List at least 5 specific top strengths from my entire resume
           - List at least 5 specific top weaknesses from my entire resume
        
        7. BULLET POINT IMPROVEMENTS
           - Take at least 3 actual bullet points from my resume
           - Provide improved versions that are more impactful and ATS-friendly
        
        8. KEYWORD ANALYSIS
           - List at least 5 industry keywords already present in my resume
           - List at least 5 important keywords missing from my resume
           - Provide at least 3 specific recommendations for incorporating missing keywords into my resume
        
        9. INDUSTRY COMPARISON
           - Provide a detailed comparison (at least 2 paragraphs) of my resume to industry standards
           - Be specific about how my resume compares to others you've seen for similar roles
        
        10. OVERALL SCORE
            - Provide an overall score for my resume from 0-100
        
        Be specific, detailed, and speak directly to me. I want actionable advice that I can start implementing immediately. Don't hold back - I need your honest assessment to improve my career prospects.
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
            ImprovedResumeOutput containing the optimized resume markdown and summary of changes
        """
        # Create system prompt with emphasis on beautiful formatting
        system_prompt = """
        I want you to act as my personal resume designer with 20+ years of experience crafting visually stunning, ATS-optimized resumes 
        for top executives and professionals. You've helped thousands of people like me land jobs at Fortune 500 companies.
        
        Your task is to completely transform MY resume into a masterpiece that combines:
        1. Compelling, achievement-oriented content that showcases my value
        2. Clean, modern design with perfect spacing and alignment
        3. Strategic keyword placement for ATS optimization
        4. Visual hierarchy that guides the reader's eye to my best qualifications
        5. Perfect balance of white space and content density
        
        The output should be in Markdown format, but you MUST use advanced Markdown formatting to create 
        a resume that looks professionally designed and represents me in the best possible light:
        
        - Use headings (# ## ###) strategically for section titles and my name
        - Use horizontal rules (---) to create visual separation
        - Use bold and italics to emphasize my key information
        - Use tables for clean alignment of dates and locations
        - Use bullet points with proper indentation hierarchies
        - Add subtle Unicode symbols (like → ● ○ ■ □) where appropriate
        - Use line breaks strategically to create proper spacing
        - Create visual distinction between sections
        
        IMPORTANT: Your response must ONLY include:
        1. The complete, detailed markdown for my improved resume
        2. A list of major changes made to improve my resume
        
        Do not include any other information or analysis in your response.
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
        I want you to transform MY resume into a professional, visually appealing document for a {job_title} position in the {industry} industry.
        
        ## MY ORIGINAL RESUME:
        {resume_text}
        
        ## ANALYSIS FINDINGS FROM MY RESUME:
        Key issues in my resume to address:
        {chr(10).join(f"- {point}" for point in improvement_points)}
        
        Key strengths in my resume to highlight:
        {chr(10).join(f"- {strength}" for strength in strengths)}
        
        ## BULLET POINT IMPROVEMENTS FOR MY RESUME:
        {bullet_point_examples}
        
        ## KEYWORD OPPORTUNITIES FOR MY RESUME:
        Missing keywords to add to my resume: {', '.join(analysis_result.keywordAnalysis.missing)}
        Existing keywords in my resume to emphasize: {', '.join(analysis_result.keywordAnalysis.matched)}
        
        ## DESIGN REQUIREMENTS FOR MY RESUME:
        Create a clean, modern resume for me with the following sections:
        
        1. HEADER
           - My name (prominently displayed)
           - My contact information (phone, email, LinkedIn, location)
           - Optional: Professional title aligned with my target job
        
        2. PROFESSIONAL SUMMARY
           - Compelling 3-4 line summary highlighting my key qualifications
           - Include top keywords from my job title and industry
           - Focus on my unique value proposition and career highlights
        
        3. SKILLS SECTION
           - Organized in categories (Technical, Professional, etc.)
           - Prioritize keywords relevant to my job
           - Include all my matched keywords and add missing keywords
        
        4. PROFESSIONAL EXPERIENCE
           - Company name, location, job title with clear formatting
           - Dates formatted consistently (MM/YYYY or YYYY)
           - Accomplishment-focused bullet points with metrics from my experience
           - Start each bullet with strong action verbs
           - Include 3-5 bullets per position, focused on my achievements
        
        5. EDUCATION
           - My degree, institution, graduation date
           - Relevant coursework or achievements if applicable
        
        6. ADDITIONAL SECTIONS (if relevant to my background)
           - My certifications
           - My projects
           - My volunteer work
           - My publications/Patents
        
        ## MARKDOWN FORMATTING GUIDELINES:
        - Use level 1 heading (#) for my name
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
        - Transform all my weak bullet points into achievement-focused statements
        - Quantify my achievements with metrics where possible (%, $, time saved)
        - Use strong action verbs at the start of each bullet
        - Eliminate first-person pronouns (I, me, my)
        - Use present tense for my current positions, past tense for my previous roles
        - Include relevant keywords naturally throughout my resume
        - Ensure all information from my original resume is preserved with proper context
        
        ## RESPONSE FORMAT:
        Your response must ONLY include:
        
        1. markdown: The complete, professionally formatted resume in markdown for me
        
        2. changesSummary: A list of 5-8 major changes you made to improve my resume
        
        IMPORTANT: The resume markdown should be complete, detailed, and professional. Include ALL relevant information from my original resume.
        
        Create the most impressive, professional-looking resume possible for me that would pass any ATS system and impress any hiring manager.
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