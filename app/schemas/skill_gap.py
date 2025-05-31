from typing import List, Optional
from pydantic import BaseModel, Field

class MatchedSkill(BaseModel):
    """Simplified matched skill output"""
    skill: str = Field(..., description="The skill name")
    level: str = Field(..., description="Proficiency level: Beginner, Intermediate, Advanced, Expert")
    evidence: str = Field(..., description="Evidence from resume showing this skill")
    meets_requirement: bool = Field(..., description="Whether this skill fully meets the job requirement")

class MissingSkill(BaseModel):
    """Simplified missing skill output"""
    skill: str = Field(..., description="The missing skill name")
    importance: str = Field(..., description="Critical, Important, or Nice-to-Have")
    why_needed: str = Field(..., description="Why this skill is needed for the role")
    learning_path: str = Field(..., description="Specific steps to learn this skill")

class ProjectRecommendation(BaseModel):
    """Simplified project recommendation"""
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="What to build and how it helps")
    skills_gained: str = Field(..., description="Comma-separated skills this project develops")
    time_estimate: str = Field(..., description="Time needed to complete")
    difficulty: str = Field(..., description="Easy, Medium, or Hard")

class SkillGapAnalysisOutput(BaseModel):
    """Simplified skill gap analysis output"""
    job_title: str = Field(..., description="The job title being analyzed")
    match_percentage: int = Field(..., description="Overall match percentage (0-100)", ge=0, le=100)
    
    # Matched skills - simplified structure
    matched_skills: List[MatchedSkill] = Field(..., description="Skills that match the job requirements")
    
    # Missing skills - simplified structure  
    missing_skills: List[MissingSkill] = Field(..., description="Skills that are missing or need improvement")
    
    # Project recommendations - simplified structure
    project_recommendations: List[ProjectRecommendation] = Field(..., description="Specific projects to build missing skills")
    
    # Simple string fields for key insights
    top_strengths: str = Field(..., description="Top 3 strengths from the resume")
    biggest_gaps: str = Field(..., description="Top 3 most critical skill gaps")
    next_steps: str = Field(..., description="Immediate actionable steps to improve candidacy")
    timeline_to_ready: str = Field(..., description="Realistic timeline to become job-ready")
    overall_assessment: str = Field(..., description="Honest assessment of current fit and potential")
