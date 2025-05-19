from typing import Dict, Optional, List
from pydantic import BaseModel, Field


class ResumeSection(BaseModel):
    """Analysis of a specific resume section"""
    strengths: List[str] = Field(..., description="Specific strengths of this section (at least 3)")
    weaknesses: List[str] = Field(..., description="Areas that need improvement in this section (at least 3)") 
    recommendations: List[str] = Field(..., description="Specific, actionable recommendations to improve this section (at least 3)")
    score: int = Field(..., description="Score from 0-100")


class KeywordAnalysis(BaseModel):
    """Keyword match analysis for ATS optimization"""
    matched: List[str] = Field(..., description="Keywords found in the resume (at least 5)")
    missing: List[str] = Field(..., description="Important keywords missing from the resume (at least 5)")
    recommendations: List[str] = Field(..., description="Specific ways to incorporate missing keywords (at least 3)")


class BulletPointExample(BaseModel):
    """Before and after examples of bullet point improvements"""
    before: str = Field(..., description="Original bullet point text")
    after: str = Field(..., description="Improved bullet point text")


class ResumeAnalysisOutput(BaseModel):
    """Simplified resume analysis output"""
    # Overall assessment
    overallFeedback: str = Field(..., description="Detailed overall assessment of the resume (at least 3 paragraphs)")
    overallScore: int = Field(..., description="Overall resume score (0-100)")
    
    # Specific sections analysis
    content: ResumeSection = Field(..., description="Analysis of the resume content")
    formatting: ResumeSection = Field(..., description="Analysis of the resume formatting and structure")
    impact: ResumeSection = Field(..., description="Analysis of how impactful the resume is")
    ats: ResumeSection = Field(..., description="Analysis of ATS compatibility")
    
    # Actionable improvements
    topStrengths: List[str] = Field(..., description="Top strengths of the resume (at least 5 specific examples)")
    topWeaknesses: List[str] = Field(..., description="Top weaknesses of the resume (at least 5 specific examples)")
    
    # Specific examples with before/after
    bulletPointExamples: List[BulletPointExample] = Field(..., description="Specific examples with before/after versions (at least 3)")
    
    # Keyword analysis
    keywordAnalysis: KeywordAnalysis = Field(..., description="Analysis of keyword optimization")
    
    # Industry comparison
    industryComparison: str = Field(..., description="Detailed comparison to industry standards (at least 2 paragraphs)")
    
    # Target information
    industry: str = Field(..., description="Industry the analysis is for")
    jobTitle: str = Field(..., description="Target job title")


class ImprovedResumeOutput(BaseModel):
    """Output model for the improved resume"""
    markdown: str = Field(..., description="Markdown formatted improved resume")
    changesSummary: List[str] = Field(..., description="Summary of changes made (at least 5)")
    improvementScore: int = Field(..., description="Estimated score improvement (0-100)")
    sectionImprovements: Dict[str, List[str]] = Field(..., description="Specific improvements made to each section")
    keywordsAdded: List[str] = Field(..., description="Keywords added to the resume")
    formattingImprovements: List[str] = Field(..., description="Formatting improvements made to the resume")
    contentImprovements: List[str] = Field(..., description="Content improvements made to the resume")
