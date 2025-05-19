from pydantic import BaseModel, Field
from typing import List, Optional

class QuestionOption(BaseModel):
    """Individual option for a multiple choice question"""
    text: str = Field(..., description="The text of the option")

class MultipleChoiceQuestion(BaseModel):
    """Multiple choice question with options"""
    id: str = Field(..., description="Unique identifier for the question")
    label: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="List of possible answers")

class NicheQuestionsOutput(BaseModel):
    """Output format for multiple choice questions based on a niche"""
    questions: List[MultipleChoiceQuestion] = Field(
        ..., 
        description="List of multiple choice questions customized for the niche"
    )

class LearningResourceOutput(BaseModel):
    """Output model for a learning resource"""
    type: str = Field(description="Type of resource (e.g., course, book, article, video, tutorial)")
    name: str = Field(description="Name of the resource")
    link: str = Field(description="URL link to the resource")
    rating: Optional[float] = Field(None, description="Rating of the resource (0-5)")
    description: Optional[str] = Field(None, description="Brief description of the resource")

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

class LearningPathOutput(BaseModel):
    """Output model for a complete learning path"""
    title: str = Field(description="Title of the learning path")
    description: str = Field(description="Detailed description of the learning path")
    estimatedTime: str = Field(description="Total estimated time to complete the path")
    modules: List[LearningModuleOutput] = Field(description="List of learning modules in this path")
    niche: str = Field(description="The industry niche or technology area for this path")
