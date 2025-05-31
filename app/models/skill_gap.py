from datetime import datetime
from typing import List, Optional, ClassVar, Any
from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.user import PyObjectId

class MatchedSkill(BaseModel):
    """Simplified matched skill model"""
    skill: str
    level: str  # Beginner, Intermediate, Advanced, Expert
    evidence: str  # Evidence from resume showing this skill
    meets_requirement: bool  # Whether this skill fully meets the job requirement
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }

class MissingSkill(BaseModel):
    """Simplified missing skill model"""
    skill: str
    importance: str  # Critical, Important, Nice-to-Have
    why_needed: str  # Why this skill is needed for the role
    learning_path: str  # Specific steps to learn this skill
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }

class ProjectRecommendation(BaseModel):
    """Simplified project recommendation model"""
    title: str
    description: str  # What to build and how it helps
    skills_gained: str  # Comma-separated skills this project develops
    time_estimate: str  # Time needed to complete
    difficulty: str  # Easy, Medium, or Hard
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }

class SkillGapAnalysisBase(BaseModel):
    """Base skill gap analysis model with simplified structure"""
    job_title: str
    job_description: str
    resume_text: str
    match_percentage: int  # 0-100 percentage
    matched_skills: List[MatchedSkill]
    missing_skills: List[MissingSkill]
    project_recommendations: List[ProjectRecommendation]
    top_strengths: str  # Top 3 strengths from the resume
    biggest_gaps: str  # Top 3 most critical skill gaps
    next_steps: str  # Immediate actionable steps to improve candidacy
    timeline_to_ready: str  # Realistic timeline to become job-ready
    overall_assessment: str  # Honest assessment of current fit and potential

class SkillGapAnalysisInDB(SkillGapAnalysisBase):
    """
    Skill gap analysis model as stored in the database
    """
    id: PyObjectId = Field(default_factory=lambda: ObjectId(), alias="_id")
    userId: PyObjectId
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    job_posting_url: Optional[str] = None
    
    model_config: ClassVar[dict] = {
        "populate_by_name": True, 
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class SkillGapAnalysis(SkillGapAnalysisBase):
    """
    Skill gap analysis model returned to client
    """
    id: str
    userId: str
    createdAt: datetime
    job_posting_url: Optional[str] = None
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }
    
class SkillGapAnalysisRequest(BaseModel):
    """
    Request model for skill gap analysis
    """
    resumeText: Optional[str] = None
    resumeFile: Optional[Any] = None  # This will be handled as UploadFile in FastAPI
    jobDescription: Optional[str] = None
    jobPostingUrl: Optional[str] = None
    githubUrl: Optional[str] = None 