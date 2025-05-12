import groq
import instructor
import json
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.core.config import settings


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


class AIService:
    def __init__(self):
        # Set up the Groq client with Instructor
        # Instructor adds structured output support to the model
        client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.client = instructor.from_groq(client)
        
        # Use Llama 3 model for generating structured outputs
        self.model = "llama-3.3-70b-versatile"
    
    def generate_learning_path(
        self, 
        niche_name: str, 
        answers: Dict[str, str]
    ) -> LearningPathOutput:
        """
        Generate a learning path using Groq AI with structured outputs
        """
        # Prepare user preferences from answers
        user_preferences = []
        for question, answer in answers.items():
            user_preferences.append(f"- {question}: {answer}")
        
        user_preferences_text = "\n".join(user_preferences)
        
        # Create the system prompt
        system_prompt = f"""
        You are an expert education advisor specializing in creating personalized learning paths.
        Your task is to create a comprehensive, detailed learning path for a student interested in {niche_name}.
        
        The learning path should be structured with modules that build on each other logically. 
        Each module should contain:
        - A clear title
        - An appropriate timeline (in weeks/months)
        - A difficulty level
        - A detailed description
        - A comprehensive list of relevant topics
        - High-quality learning resources (courses, books, videos, etc.)
        - Practical tips for success
        
        Learning resources should be real, accessible online resources with accurate links.
        Include a mix of free and paid resources, focusing on quality and relevance.
        
        The overall path should have a clear progression, from foundational to advanced topics,
        and should be tailored to the user's specific preferences.
        """
        
        # Create the user prompt
        user_prompt = f"""
        Please create a detailed learning path for {niche_name} based on my preferences:
        
        {user_preferences_text}
        
        The learning path should:
        1. Be comprehensive and well-structured
        2. Include real, accessible learning resources with links
        3. Provide a clear progression from basics to advanced topics
        4. Be realistic in terms of timeline and learning curve
        5. Include practical tips for each module
        """
        
        # Generate the learning path with structured output
        try:
            # Use the instance client directly now that we've removed async
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=LearningPathOutput,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
            )
            
            return response
        except Exception as e:
            # Log error and raise
            print(f"Error generating learning path: {str(e)}")
            raise
