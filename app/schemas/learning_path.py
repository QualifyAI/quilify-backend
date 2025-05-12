from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.models.learning_resource import LearningResource
from app.models.learning_path import Niche, PathQuestion, LearningModule, LearningPath


class LearningPathRequest(BaseModel):
    """
    Request model for generating a learning path
    """
    nicheId: int
    customNiche: Optional[str] = None
    answers: Dict[str, str]


class LearningPathGenerationResponse(BaseModel):
    """
    Response model for the generated learning path
    """
    path: LearningPath
    

class LearningResourceCreate(LearningResource):
    """
    Model for creating a learning resource
    """
    pass


class LearningModuleCreate(BaseModel):
    """
    Model for creating a learning module
    """
    id: int
    title: str
    timeline: str
    difficulty: str
    description: str
    topics: List[str]
    resources: List[LearningResourceCreate]
    tips: str
    

class LearningPathCreate(BaseModel):
    """
    Model for creating a learning path
    """
    title: str
    description: str
    estimatedTime: str
    modules: List[LearningModuleCreate]
    niche: str
