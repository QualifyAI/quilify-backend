from datetime import datetime
from typing import List, Optional, ClassVar, Any
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
    progress: Optional[float] = 0
    
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
    

class LearningPathInDB(LearningPathBase):
    """
    Learning path model as stored in the database
    """
    id: PyObjectId = Field(default_factory=lambda: ObjectId(), alias="_id")
    userId: PyObjectId
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = None
    
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
    
    model_config: ClassVar[dict] = {
        "from_attributes": True
    } 