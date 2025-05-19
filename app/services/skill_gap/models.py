from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class SkillMatchOutput(BaseModel):
    """
    Output schema for a matched skill
    """
    skill: str = Field(..., description="The name of the skill that was matched")
    level: str = Field(..., description="The level of proficiency demonstrated in the resume (Expert, Advanced, Intermediate, Beginner)")
    match_score: float = Field(..., description="A score from 0 to 1 indicating how well the skill matches the job requirement", ge=0, le=1)
    context: Optional[str] = Field(None, description="Relevant context from the resume where this skill was demonstrated")

class SkillGapOutput(BaseModel):
    """
    Output schema for a missing skill
    """
    skill: str = Field(..., description="The name of the skill that is missing or underdeveloped")
    importance: str = Field(..., description="How important this skill is for the job (Critical, Important, Nice to have)")
    description: str = Field(..., description="Description of the skill and why it's important for the role")
    learning_resources: List[Dict[str, str]] = Field(..., description="List of resources to help learn this skill (books, courses, tutorials)")

class ProjectRecommendationOutput(BaseModel):
    """
    Output schema for a recommended project
    """
    title: str = Field(..., description="Title of the recommended project")
    description: str = Field(..., description="Detailed description of the project and what it involves")
    skills_addressed: List[str] = Field(..., description="List of skills this project will help develop")
    difficulty: str = Field(..., description="Difficulty level of the project (Easy, Moderate, Challenging)")
    estimated_time: str = Field(..., description="Estimated time to complete the project")
    resources: List[Dict[str, str]] = Field(..., description="List of resources to help with the project")

class SkillGapAnalysisOutput(BaseModel):
    """
    Output schema for the complete skill gap analysis
    """
    job_title: str = Field(..., description="The title of the job being analyzed")
    match_percentage: float = Field(..., description="Overall match percentage between the resume and job requirements", ge=0, le=100)
    matched_skills: List[SkillMatchOutput] = Field(..., description="List of skills that match between the resume and job requirements")
    missing_skills: List[SkillGapOutput] = Field(..., description="List of skills that are missing or underdeveloped")
    project_recommendations: List[ProjectRecommendationOutput] = Field(..., description="Recommended projects to build to address skill gaps")
    improvement_suggestions: Dict[str, List[str]] = Field(..., description="Specific suggestions for improving various aspects of the resume")
    overall_assessment: str = Field(..., description="An overall assessment of the candidate's fit for the job")
