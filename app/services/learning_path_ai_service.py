import os
import instructor
from typing import Dict, List, Optional
from groq import Groq
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.learning_path import PathQuestion

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




class LearningPathAIService:
    def __init__(self):
        # Defer initialization to when methods are actually called
        self.groq_client = None
        self.client = None
        # Use LLama 3.3 70B for optimal performance
        self.model = "llama-3.3-70b-versatile"
    
    def _ensure_client_initialized(self):
        """Lazily initialize the Groq client only when needed"""
        if not self.groq_client:
            # Initialize Groq client
            self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
            # Patch with instructor for structured outputs
            self.client = instructor.from_groq(self.groq_client)
    
    async def generate_questions_for_niche(self, niche_name: str) -> List[PathQuestion]:
        """
        Generate multiple choice questions for tailoring a learning path 
        based on the selected niche
        """
        # Ensure client is initialized
        self._ensure_client_initialized()
        
        # Create the system prompt
        system_prompt = """
        You are an expert education curriculum designer with deep expertise in personalized learning paths. 
        Your task is to create highly relevant multiple-choice questions that will help determine a user's 
        specific needs, experience level, and goals within their chosen field of interest.
        
        Each question should:
        1. Be directly relevant to the specific niche/industry provided
        2. Have 4-5 distinct multiple choice options that represent different approaches, experience levels, or preferences
        3. Help determine the user's specific learning needs, goals, or current skill level
        4. Be unbiased and inclusive, accommodating different learning styles and backgrounds
        5. Use clear, concise language appropriate for all educational levels
        
        Your questions should cover varied aspects including:
        - Current experience/skill level in the field
        - Specific goals and aspirations
        - Learning preferences and style
        - Time commitment and availability
        - Areas of particular interest within the broader field
        - Practical application vs theoretical knowledge preference
        
        Make sure each question provides genuinely useful information that would help create a 
        tailored learning path for the user.
        """
        
        # Create the user prompt
        user_prompt = f"""
        Please generate 5-8 multiple choice questions for a user interested in the "{niche_name}" field.
        
        These questions will be used to customize a learning path specifically for this user based on 
        their experience level, goals, and preferences.
        
        For each question:
        - Create a clear, concise question statement
        - Provide 4-5 distinct answer options that represent different approaches or preferences
        - Ensure the options cover a range of possibilities (beginner to advanced, practical to theoretical, etc.)
        - Make sure the question will provide useful information for customizing a learning journey
        
        Format the response as structured data according to the required schema.
        """
        
        # Make request to Groq
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=NicheQuestionsOutput,
                messages=messages,
                temperature=0.3,  # Low temperature for consistent, focused results
       
            )
            
            # Convert to PathQuestion model
            return [
                PathQuestion(
                    id=q.id,
                    label=q.label,
                    options=q.options
                ) for q in response.questions
            ]
        except Exception as e:
            print(f"Error generating questions with Groq API: {e}")
            # Return a fallback set of generic questions
            return self._generate_fallback_questions(niche_name)
    
    def _generate_fallback_questions(self, niche_name: str) -> List[PathQuestion]:
        """Generate fallback questions if API call fails"""
        return [
            PathQuestion(
                id="experience_level",
                label=f"What is your current experience level in {niche_name}?",
                options=[
                    "Complete beginner with no experience",
                    "Beginner with some basic knowledge",
                    "Intermediate with practical experience",
                    "Advanced with significant experience",
                    "Expert looking to specialize further"
                ]
            ),
            PathQuestion(
                id="learning_goal",
                label=f"What is your primary goal for learning about {niche_name}?",
                options=[
                    "Career transition into this field",
                    "Skill enhancement for current role",
                    "Personal interest and growth",
                    "Academic requirement or research",
                    "Entrepreneurial venture or project"
                ]
            ),
            PathQuestion(
                id="time_commitment",
                label="How much time can you commit to learning each week?",
                options=[
                    "Less than 5 hours",
                    "5-10 hours",
                    "10-20 hours",
                    "20+ hours",
                    "Flexible/variable schedule"
                ]
            ),
            PathQuestion(
                id="learning_style",
                label="What learning approach do you prefer?",
                options=[
                    "Hands-on projects and practical application",
                    "Video courses and tutorials",
                    "Reading books and documentation",
                    "Interactive exercises and quizzes",
                    "Combination of different methods"
                ]
            ),
            PathQuestion(
                id="application_focus",
                label=f"How do you plan to apply your {niche_name} knowledge?",
                options=[
                    "Building personal projects",
                    "Applying to jobs in this field",
                    "Solving specific problems at work",
                    "Teaching or mentoring others",
                    "Exploring innovative ideas"
                ]
            )
        ]
    
    

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
            # Process custom answers
            if answer.startswith('custom:'):
                # Extract the custom text after 'custom:'
                cleaned_answer = answer[7:]  # Skip 'custom:'
                user_preferences.append(f"- {question}: {cleaned_answer} (custom response)")
            else:
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
            )
            
            return response
        except Exception as e:
            # Log error and raise
            print(f"Error generating learning path: {str(e)}")
            raise
 