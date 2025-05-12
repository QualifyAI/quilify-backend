from datetime import datetime
from typing import List, Optional, ClassVar, Dict, Any
from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.user import PyObjectId

class SkillMatch(BaseModel):
    """
    Represents a match between a user's skill and a job requirement
    """
    skill: str
    level: str  # e.g., "Expert", "Intermediate", "Beginner"
    match_score: float  # 0-1 score indicating how well the skill matches
    context: Optional[str] = None  # Context from resume where skill was found
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }

class SkillGap(BaseModel):
    """
    Represents a missing or underdeveloped skill
    """
    skill: str
    importance: str  # e.g., "Critical", "Important", "Nice to have"
    description: str
    learning_resources: List[Dict[str, str]]  # List of resources to learn the skill
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }

class ProjectRecommendation(BaseModel):
    """
    Recommended project to build to address skill gaps
    """
    title: str
    description: str
    skills_addressed: List[str]
    difficulty: str
    estimated_time: str
    resources: List[Dict[str, str]]
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }

class SkillGapAnalysisBase(BaseModel):
    """
    Base skill gap analysis model
    """
    job_title: str
    job_description: str
    resume_text: str
    match_percentage: float
    matched_skills: List[SkillMatch]
    missing_skills: List[SkillGap]
    project_recommendations: List[ProjectRecommendation]
    improvement_suggestions: Dict[str, List[str]]
    overall_assessment: str
    

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