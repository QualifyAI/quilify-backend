from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class NicheQuestionOutput(BaseModel):
    """Single question for learning path personalization"""
    id: str = Field(description="Unique identifier for the question (e.g., 'experience_level')")
    label: str = Field(description="The question text to display to the user")
    options: List[str] = Field(description="List of 4-5 possible answer options")

class NicheQuestionsOutput(BaseModel):
    """Output model for questions about a learning path niche"""
    questions: List[NicheQuestionOutput] = Field(description="List of questions to tailor the learning path")

class LearningResourceOutput(BaseModel):
    """Output model for a learning resource"""
    type: str = Field(description="Type of resource (e.g., course, book, article, video, tutorial)")
    name: str = Field(description="Name of the resource")
    link: str = Field(description="URL link to the resource")
    rating: Optional[float] = Field(None, description="Rating of the resource (0-5)")
    description: Optional[str] = Field(None, description="Brief description of the resource")
    isFree: bool = Field(default=True, description="Whether the resource is free or paid")
    estimatedTime: Optional[str] = Field(None, description="Estimated time to complete this resource")

class SubTopic(BaseModel):
    """A subtopic within a learning module"""
    title: str = Field(description="Title of the subtopic")
    description: str = Field(description="Detailed explanation of the subtopic")
    resources: List[LearningResourceOutput] = Field(description="Specific resources for learning this subtopic")

class LearningModuleOutput(BaseModel):
    """Output model for a learning module"""
    id: int = Field(description="Unique ID for the module")
    title: str = Field(description="Title of the learning module")
    timeline: str = Field(description="Estimated time to complete the module (e.g., '2 weeks')")
    difficulty: str = Field(description="Difficulty level (Beginner, Intermediate, Advanced)")
    description: str = Field(description="Detailed description of the module")
    topics: List[str] = Field(description="List of topics covered in this module")
    resources: List[LearningResourceOutput] = Field(description="List of learning resources for this module")
    tips: str = Field(description="Tips or advice for learning this module effectively")
    subtopics: Optional[List[SubTopic]] = Field(None, description="Detailed breakdown of subtopics in this module")
    prerequisites: Optional[List[str]] = Field(None, description="Prerequisites needed before starting this module")
    learningObjectives: Optional[List[str]] = Field(None, description="Specific learning objectives for this module")
    projects: Optional[List[str]] = Field(None, description="Suggested projects to reinforce learning")

class LearningPathOutput(BaseModel):
    """Output model for a complete learning path"""
    title: str = Field(description="Title of the learning path")
    description: str = Field(description="Detailed description of the learning path")
    estimatedTime: str = Field(description="Total estimated time to complete the path")
    modules: List[LearningModuleOutput] = Field(description="List of learning modules in this path")
    niche: str = Field(description="The industry niche or technology area for this path")
    overview: Optional[str] = Field(None, description="Comprehensive overview of the learning journey")
    prerequisites: Optional[List[str]] = Field(None, description="General prerequisites for the entire learning path")
    intendedAudience: Optional[str] = Field(None, description="Description of who this learning path is designed for")
    careerOutcomes: Optional[List[str]] = Field(None, description="Potential career outcomes after completing this path")

class DetailedModuleOutput(BaseModel):
    """Output model for a detailed module expansion"""
    moduleId: int = Field(description="ID of the module being detailed")
    subtopics: List[SubTopic] = Field(description="Detailed breakdown of subtopics in this module")
    prerequisites: List[str] = Field(description="Prerequisites needed before starting this module")
    learningObjectives: List[str] = Field(description="Specific learning objectives for this module")
    projects: List[str] = Field(description="Suggested projects to reinforce learning")
    detailedDescription: str = Field(description="Expanded in-depth description of the module")

class ResourceVerificationOutput(BaseModel):
    """Output model for verified resources"""
    moduleId: int = Field(description="ID of the module these resources are for")
    resources: List[LearningResourceOutput] = Field(description="List of verified free learning resources")
