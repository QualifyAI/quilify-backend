from datetime import datetime
from typing import List, Optional, ClassVar, Any, Dict
from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.learning_resource import LearningResource
from app.models.user import PyObjectId


class Niche(BaseModel):
    """
    Industry or technology niche for learning paths
    """
    id: int
    name: str
    icon: str
    description: str
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }


class PathQuestion(BaseModel):
    """
    Question to customize the learning path
    """
    id: str
    label: str
    options: List[str]
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }


class LearningResourceProgress(BaseModel):
    """
    Progress tracking for individual learning resources
    """
    resource_id: str  # Unique identifier for the resource
    completed: bool = False
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    rating: Optional[int] = None  # 1-5 star rating
    time_spent_minutes: Optional[int] = None
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }


class LearningModule(BaseModel):
    """
    Module within a learning path containing resources and topics
    """
    id: int
    title: str
    timeline: str  # e.g. "2 weeks"
    difficulty: str  # e.g. "Beginner", "Intermediate", "Advanced"
    description: str
    topics: List[str]
    resources: List[LearningResource]
    tips: str
    completed: Optional[bool] = False
    progress: Optional[float] = 0  # 0-100 percentage
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    notes: Optional[str] = None
    resource_progress: Optional[List[LearningResourceProgress]] = []
    custom_resources: Optional[List[LearningResource]] = []  # User-added resources
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }


class LearningPathStats(BaseModel):
    """
    Statistics and analytics for a learning path
    """
    total_modules: int = 0
    completed_modules: int = 0
    total_resources: int = 0
    completed_resources: int = 0
    total_time_spent_minutes: int = 0
    estimated_completion_date: Optional[datetime] = None
    last_activity_date: Optional[datetime] = None
    average_module_completion_days: Optional[float] = None
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }


class LearningPathBase(BaseModel):
    """
    Base learning path model
    """
    title: str
    description: str
    estimatedTime: str
    modules: List[LearningModule]
    niche: str
    is_active: Optional[bool] = True
    target_completion_date: Optional[datetime] = None
    custom_notes: Optional[str] = None
    stats: Optional[LearningPathStats] = None
    

class LearningPathInDB(LearningPathBase):
    """
    Learning path model as stored in the database
    """
    id: PyObjectId = Field(default_factory=lambda: ObjectId(), alias="_id")
    userId: PyObjectId
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    
    model_config: ClassVar[dict] = {
        "populate_by_name": True, 
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class LearningPath(LearningPathBase):
    """
    Learning path model returned to client
    """
    id: str
    userId: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    }


# New models for progress tracking API requests
class ModuleProgressUpdate(BaseModel):
    """
    Request model for updating module progress
    """
    module_id: int
    completed: Optional[bool] = None
    progress: Optional[float] = None
    notes: Optional[str] = None
    target_completion_date: Optional[datetime] = None


class ResourceProgressUpdate(BaseModel):
    """
    Request model for updating resource progress
    """
    module_id: int
    resource_id: str
    completed: Optional[bool] = None
    notes: Optional[str] = None
    rating: Optional[int] = None
    time_spent_minutes: Optional[int] = None


class CustomResourceAdd(BaseModel):
    """
    Request model for adding custom resources to a module
    """
    module_id: int
    resource: LearningResource 