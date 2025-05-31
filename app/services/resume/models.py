from typing import Dict, Optional, List
from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of a specific scoring category"""
    score: int = Field(..., description="Score from 0-100", ge=0, le=100)
    strengths: List[str] = Field(..., description="Specific strengths identified (at least 3)")
    weaknesses: List[str] = Field(..., description="Areas needing improvement (at least 3)")
    recommendations: List[str] = Field(..., description="Actionable recommendations (at least 3)")
    examples: List[str] = Field(default=[], description="Specific examples from the resume")


class ATSCompatibilityScore(BaseModel):
    """ATS compatibility analysis with specific technical details"""
    score: int = Field(..., description="Overall ATS score (0-100)", ge=0, le=100)
    keyword_optimization: int = Field(..., description="Keyword optimization score", ge=0, le=100)
    format_compatibility: int = Field(..., description="Format compatibility score", ge=0, le=100)
    section_structure: int = Field(..., description="Section structure score", ge=0, le=100)
    file_format_score: int = Field(..., description="File format appropriateness", ge=0, le=100)
    
    # Detailed feedback
    strengths: List[str] = Field(default=[], description="ATS-friendly elements")
    issues: List[str] = Field(default=[], description="ATS compatibility issues")
    recommendations: List[str] = Field(default=[], description="Specific ATS improvements")
    
    # Keyword analysis - make optional with defaults
    matched_keywords: List[str] = Field(default=[], description="Industry keywords found")
    missing_keywords: List[str] = Field(default=[], description="Important missing keywords")
    keyword_density: float = Field(default=0.0, description="Keyword density percentage")


class ContentQualityScore(BaseModel):
    """Content quality analysis focusing on impact and achievements"""
    score: int = Field(..., description="Overall content score (0-100)", ge=0, le=100)
    achievement_focus: int = Field(..., description="Achievement vs responsibility focus", ge=0, le=100)
    quantification: int = Field(..., description="Use of metrics and numbers", ge=0, le=100)
    action_verbs: int = Field(..., description="Strong action verb usage", ge=0, le=100)
    relevance: int = Field(..., description="Relevance to target role", ge=0, le=100)
    
    # Detailed analysis
    strengths: List[str] = Field(default=[], description="Content strengths")
    weaknesses: List[str] = Field(default=[], description="Content weaknesses")
    recommendations: List[str] = Field(default=[], description="Content improvements")
    
    # Specific examples
    strong_bullets: List[str] = Field(default=[], description="Well-written bullet points")
    weak_bullets: List[str] = Field(default=[], description="Bullet points needing improvement")
    quantified_achievements: List[str] = Field(default=[], description="Quantified accomplishments found")


class FormatStructureScore(BaseModel):
    """Format and structure analysis"""
    score: int = Field(..., description="Overall format score (0-100)", ge=0, le=100)
    visual_hierarchy: int = Field(..., description="Visual hierarchy clarity", ge=0, le=100)
    consistency: int = Field(..., description="Formatting consistency", ge=0, le=100)
    readability: int = Field(..., description="Overall readability", ge=0, le=100)
    length_appropriateness: int = Field(..., description="Resume length appropriateness", ge=0, le=100)
    
    # Detailed feedback
    strengths: List[str] = Field(default=[], description="Format strengths")
    issues: List[str] = Field(default=[], description="Format issues")
    recommendations: List[str] = Field(default=[], description="Format improvements")


class ImpactScore(BaseModel):
    """Overall impact and effectiveness analysis"""
    score: int = Field(..., description="Overall impact score (0-100)", ge=0, le=100)
    first_impression: int = Field(..., description="First impression strength", ge=0, le=100)
    differentiation: int = Field(..., description="How well it differentiates candidate", ge=0, le=100)
    value_proposition: int = Field(..., description="Clear value proposition", ge=0, le=100)
    memorability: int = Field(..., description="How memorable the resume is", ge=0, le=100)
    
    # Detailed analysis
    strengths: List[str] = Field(default=[], description="Impact strengths")
    weaknesses: List[str] = Field(default=[], description="Impact weaknesses")
    recommendations: List[str] = Field(default=[], description="Impact improvements")


class BulletPointExample(BaseModel):
    """Before and after examples of bullet point improvements"""
    original: str = Field(..., description="Original bullet point text")
    improved: str = Field(..., description="Improved bullet point text")
    explanation: str = Field(..., description="Why the improvement is better")
    impact_increase: int = Field(..., description="Estimated impact increase percentage")


class IndustryBenchmark(BaseModel):
    """Industry-specific benchmarking analysis"""
    industry: str = Field(..., description="Target industry")
    percentile_ranking: int = Field(..., description="Percentile ranking vs industry peers", ge=0, le=100)
    competitive_advantages: List[str] = Field(default=[], description="Competitive advantages identified")
    improvement_priorities: List[str] = Field(default=[], description="Top improvement priorities for industry")
    industry_specific_feedback: str = Field(default="", description="Industry-specific detailed feedback")


class ResumeAnalysisOutput(BaseModel):
    """Comprehensive resume analysis with detailed scoring and actionable insights"""
    
    # Overall Assessment
    overall_score: int = Field(..., description="Overall resume score (0-100)", ge=0, le=100)
    overall_feedback: str = Field(..., description="Comprehensive overall assessment (at least 4 paragraphs)")
    
    # Detailed Score Breakdowns
    ats_compatibility: ATSCompatibilityScore = Field(..., description="ATS compatibility analysis")
    content_quality: ContentQualityScore = Field(..., description="Content quality analysis")
    format_structure: FormatStructureScore = Field(..., description="Format and structure analysis")
    impact_effectiveness: ImpactScore = Field(..., description="Impact and effectiveness analysis")
    
    # Summary Scores (for dashboard/quick view)
    ats_score: int = Field(..., description="ATS compatibility summary score", ge=0, le=100)
    content_score: int = Field(..., description="Content quality summary score", ge=0, le=100)
    format_score: int = Field(..., description="Format structure summary score", ge=0, le=100)
    impact_score: int = Field(..., description="Impact effectiveness summary score", ge=0, le=100)
    
    # Actionable Improvements
    top_strengths: List[str] = Field(default=[], description="Top 5 resume strengths")
    critical_improvements: List[str] = Field(default=[], description="Top 5 critical improvements needed")
    quick_wins: List[str] = Field(default=[], description="Easy improvements with high impact")
    
    # Specific Examples
    bullet_improvements: List[BulletPointExample] = Field(default=[], description="Specific bullet point improvements (at least 5)")
    
    # Industry Context
    industry_benchmark: IndustryBenchmark = Field(..., description="Industry-specific benchmarking")
    
    # Target Information
    target_job_title: str = Field(..., description="Target job title analyzed for")
    target_industry: str = Field(..., description="Target industry analyzed for")
    
    # Metadata
    analysis_date: str = Field(..., description="Date of analysis")
    estimated_improvement_potential: int = Field(..., description="Estimated score improvement potential", ge=0, le=100)


class ImprovedResumeOutput(BaseModel):
    """Enhanced output model for optimized resume"""
    markdown: str = Field(..., description="Markdown formatted improved resume")
    changes_summary: List[str] = Field(..., description="Summary of key changes made")
    improvement_score: int = Field(..., description="Estimated improvement in overall score", ge=0, le=100)
    before_after_comparison: Dict[str, Dict[str, int]] = Field(..., description="Before/after score comparison")
    implementation_guide: List[str] = Field(..., description="Step-by-step implementation guide")


class SimpleImprovedResumeOutput(BaseModel):
    """Simplified output model for optimized resume - just enhanced text"""
    markdown: str = Field(..., description="Markdown formatted improved resume")
    changes_summary: List[str] = Field(..., description="Summary of key changes made (3-5 items)")
    improvement_score: int = Field(..., description="Estimated improvement in overall score", ge=0, le=100)
