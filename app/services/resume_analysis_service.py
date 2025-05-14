import os
import instructor
from typing import Dict, Optional, List, Any
from groq import Groq
from pydantic import BaseModel, Field

from app.core.config import settings

# Define the structured output models
class QuantifyImpactScore(BaseModel):
    """Score for quantifying impact in resume"""
    score: int = Field(..., description="Score from 0-100")
    quantifiedBullets: List[str] = Field(..., description="Bullets with quantifiable metrics")
    nonQuantifiedBullets: List[str] = Field(..., description="Bullets lacking quantifiable metrics")
    improvementSuggestions: List[str] = Field(..., description="Specific suggestions to add metrics")

class ActionVerbScore(BaseModel):
    """Score for action verb usage"""
    score: int = Field(..., description="Score from 0-100")
    strongVerbs: List[str] = Field(..., description="Strong action verbs used")
    weakVerbs: List[str] = Field(..., description="Weak verbs that should be replaced")
    recommendedAlternatives: Dict[str, List[str]] = Field(..., description="Recommended alternatives for weak verbs")

class TenseConsistencyScore(BaseModel):
    """Score for verb tense consistency"""
    score: int = Field(..., description="Score from 0-100")
    inconsistencies: List[str] = Field(..., description="Tense inconsistencies found")
    recommendations: List[str] = Field(..., description="Recommendations for maintaining consistent tenses")

class AccomplishmentScore(BaseModel):
    """Score for accomplishment-oriented language"""
    score: int = Field(..., description="Score from 0-100")
    responsibilityStatements: List[str] = Field(..., description="Statements focusing only on responsibilities")
    accomplishmentStatements: List[str] = Field(..., description="Statements highlighting accomplishments")
    transformationSuggestions: Dict[str, str] = Field(..., description="How to transform responsibilities into accomplishments")

class ImpactScore(BaseModel):
    """Overall impact score"""
    quantifyImpact: QuantifyImpactScore = Field(..., description="Score for quantifying impact")
    actionVerbs: ActionVerbScore = Field(..., description="Score for action verb usage")
    tenseConsistency: TenseConsistencyScore = Field(..., description="Score for verb tense consistency")
    accomplishmentOrientation: AccomplishmentScore = Field(..., description="Score for accomplishment-oriented language")
    overallScore: int = Field(..., description="Overall impact score (0-100)")

class BrevityScore(BaseModel):
    """Brevity and conciseness score"""
    bulletPointUsage: int = Field(..., description="Score for effective use of bullet points (0-100)")
    bulletPointLength: int = Field(..., description="Score for optimal bullet point length (0-100)")
    fillerWordUsage: int = Field(..., description="Score for minimizing filler words (0-100)")
    pageDensity: int = Field(..., description="Score for appropriate page density (0-100)")
    overallScore: int = Field(..., description="Overall brevity score (0-100)")
    suggestions: List[str] = Field(..., description="Suggestions to improve brevity")

class StyleScore(BaseModel):
    """Style and professionalism score"""
    buzzwordUsage: int = Field(..., description="Score for avoiding buzzwords/clichés (0-100)")
    dateFormatting: int = Field(..., description="Score for consistent date formatting (0-100)")
    contactDetails: int = Field(..., description="Score for appropriate contact information (0-100)")
    readability: int = Field(..., description="Score for overall readability (0-100)")
    personalPronouns: int = Field(..., description="Score for avoiding personal pronouns (0-100)")
    activeVoice: int = Field(..., description="Score for using active voice (0-100)")
    bulletConsistency: int = Field(..., description="Score for consistent bullet formatting (0-100)")
    overallScore: int = Field(..., description="Overall style score (0-100)")
    suggestions: List[str] = Field(..., description="Suggestions to improve style")

class SectionScore(BaseModel):
    """Section completeness and organization score"""
    experienceSections: int = Field(..., description="Score for experience sections (0-100)")
    educationSection: int = Field(..., description="Score for education section (0-100)")
    skillsSection: int = Field(..., description="Score for skills section (0-100)")
    unnecessarySections: List[str] = Field(..., description="Unnecessary sections that could be removed")
    overallScore: int = Field(..., description="Overall sections score (0-100)")
    suggestions: List[str] = Field(..., description="Suggestions to improve sections")

class SoftSkillsScore(BaseModel):
    """Soft skills demonstration score"""
    communication: int = Field(..., description="Score for demonstrating communication skills (0-100)")
    analyticalThinking: int = Field(..., description="Score for demonstrating analytical skills (0-100)")
    teamwork: int = Field(..., description="Score for demonstrating teamwork (0-100)")
    overallScore: int = Field(..., description="Overall soft skills score (0-100)")
    suggestions: List[str] = Field(..., description="Suggestions to better demonstrate soft skills")

class ATSScore(BaseModel):
    """ATS compatibility score"""
    keywordRelevance: int = Field(..., description="Score for keyword optimization (0-100)")
    jobMatch: int = Field(..., description="Score for matching job requirements (0-100)")
    formatCompatibility: int = Field(..., description="Score for ATS-friendly formatting (0-100)")
    overallScore: int = Field(..., description="Overall ATS score (0-100)")
    suggestions: List[str] = Field(..., description="Suggestions to improve ATS compatibility")

class ContentIssue(BaseModel):
    """Content issue identified in the resume"""
    type: str = Field(..., description="Type of content issue")
    instances: int = Field(..., description="Number of instances found")
    examples: List[str] = Field(..., description="Examples of the issue from the resume")
    recommendations: List[str] = Field(..., description="Specific recommendations to fix the issues")

class ATSIssue(BaseModel):
    """ATS compatibility issue"""
    type: str = Field(..., description="Type of ATS issue (Formatting, Fonts, Headers, etc)")
    issue: str = Field(..., description="Description of the issue")
    impact: str = Field(..., description="Impact level (High, Medium, Low)")
    solution: str = Field(..., description="Specific solution to fix the issue")

class KeywordAnalysis(BaseModel):
    """Keyword match analysis for ATS optimization"""
    matched: List[str] = Field(..., description="Keywords found in the resume")
    missing: List[str] = Field(..., description="Important keywords missing from the resume")
    recommendations: List[str] = Field(..., description="Recommendations for keyword optimization")

class ExampleBulletPoint(BaseModel):
    """Before and after examples of bullet point improvements"""
    before: str = Field(..., description="Original bullet point")
    after: str = Field(..., description="Improved bullet point")

class SectionAnalysis(BaseModel):
    """Analysis of a specific resume section"""
    score: int = Field(..., description="Score from 0-100")
    feedback: str = Field(..., description="Detailed feedback on this section")
    suggestions: List[str] = Field(..., description="List of specific improvement suggestions")
    beforeExample: Optional[str] = Field(None, description="Example of original content")
    afterExample: Optional[str] = Field(None, description="Example of improved content")
    bulletPoints: Optional[List[ExampleBulletPoint]] = Field(None, description="Example bullet point improvements")

class IndustryBenchmark(BaseModel):
    """Comparison to industry standards"""
    overallRanking: str = Field(..., description="Percentile ranking compared to industry standards")
    topAreaForImprovement: str = Field(..., description="Top area that would provide the biggest improvement")
    competitiveEdge: str = Field(..., description="Area where the resume has a competitive advantage")

class ResumeAnalysisOutput(BaseModel):
    """Complete resume analysis output"""
    impact: ImpactScore = Field(..., description="Impact scores")
    brevity: BrevityScore = Field(..., description="Brevity scores")
    style: StyleScore = Field(..., description="Style scores")
    sections: SectionScore = Field(..., description="Section scores")
    softSkills: SoftSkillsScore = Field(..., description="Soft skills demonstration scores")
    ats: ATSScore = Field(..., description="ATS compatibility scores")
    
    # Summary scores
    atsScore: int = Field(..., description="Overall ATS compatibility score (0-100)")
    formatScore: int = Field(..., description="Overall format and structure score (0-100)")
    contentScore: int = Field(..., description="Overall content quality score (0-100)")
    overallScore: int = Field(..., description="Overall resume score (0-100)")
    
    # Target information
    industry: str = Field(..., description="Industry the analysis is for")
    jobTitle: str = Field(..., description="Target job title")
    
    # Section-specific detailed analysis
    sectionAnalysis: Dict[str, SectionAnalysis] = Field(..., description="detailed analysis of each resume section")
    atsIssues: List[ATSIssue] = Field(..., description="detailed ATS compatibility issues upto 5 issues min")
    keywordMatch: KeywordAnalysis = Field(..., description="detailed keyword analysis. must include atleast 10 keywords")
    contentIssues: List[ContentIssue] = Field(..., description="detailed content quality issues upto 5 issues min")
    industryBenchmark: IndustryBenchmark = Field(..., description="Industry benchmark comparison")

class ImprovedResumeOutput(BaseModel):
    """Output model for the improved resume"""
    markdown: str = Field(..., description="Markdown formatted improved resume")
    changesSummary: List[str] = Field(..., description="Summary of changes made")
    improvementScore: int = Field(..., description="Estimated score improvement (0-100)")


class ResumeAnalysisService:
    def __init__(self):
        # Defer initialization to when methods are actually called
        self.groq_client = None
        self.client = None
        # Use LLama 3.3 70B for optimal performance
        self.model = "llama-3.3-70b-versatile"
    
    def _ensure_client_initialized(self):
        """Lazily initialize the Groq client only when needed"""
        if not self.groq_client:
            # Initialize Groq client
            self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
            # Patch with instructor for structured outputs
            self.client = instructor.from_groq(self.groq_client)
    
    async def analyze_resume(
        self, 
        resume_text: str, 
        job_title: str,
        industry: str
    ) -> ResumeAnalysisOutput:
        """
        Analyze a resume for ATS compatibility, content quality, and overall effectiveness
        """
        # Ensure client is initialized
        self._ensure_client_initialized()
        
        # Create the system prompt
        system_prompt = f"""
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
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=ResumeAnalysisOutput,
                messages=messages,
                temperature=0.3,  # Lower temperature for more focused, consistent results
            )
            print("response", response)
            return response
        except Exception as e:
            print(f"Error from Groq API: {e}")
            raise
    
    async def optimize_resume(
        self, 
        resume_text: str,
        job_title: str,
        industry: str,
        analysis_result: ResumeAnalysisOutput
    ) -> ImprovedResumeOutput:
        """
        Generate an optimized version of the resume based on the analysis
        """
        # Ensure client is initialized
        self._ensure_client_initialized()
        
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
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=ImprovedResumeOutput,
                messages=messages,
                temperature=0.4,  # Slightly higher temperature for creativity in writing
            )
            print("response", response)
            return response
        except Exception as e:
            print(f"Error from Groq API: {e}")
            raise 