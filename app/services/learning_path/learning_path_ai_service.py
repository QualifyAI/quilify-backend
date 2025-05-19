from typing import Dict, List, Optional
from app.services.learning_path.models import NicheQuestionsOutput, LearningPathOutput
from app.services.ai.base_ai_service import BaseAIService
from app.models.learning_path import PathQuestion


class LearningPathAIService(BaseAIService):
    """Service for generating AI-based learning paths and related questions"""
    
    async def generate_questions_for_niche(self, niche_name: str) -> List[PathQuestion]:
        """
        Generate multiple choice questions for tailoring a learning path 
        based on the selected niche
        
        Args:
            niche_name: The name of the niche/industry
            
        Returns:
            List of PathQuestion objects with generated questions
        """
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
        try:
            response = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=NicheQuestionsOutput,
                temperature=0.3
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
            # Fall back to generating standard questions
            print(f"Error generating questions with Groq API: {str(e)}")
            return self._generate_fallback_questions(niche_name)
    
    def _generate_fallback_questions(self, niche_name: str) -> List[PathQuestion]:
        """
        Generate fallback questions if API call fails
        
        Args:
            niche_name: The name of the niche/industry
            
        Returns:
            List of standard PathQuestion objects
        """
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
                id="expertise_focus",
                label=f"Which aspect of {niche_name} are you most interested in?",
                options=[
                    "Fundamental principles and theory",
                    "Practical implementation and tools",
                    "Advanced techniques and specialization",
                    "Industry best practices and standards",
                    "Innovation and emerging trends"
                ]
            )
        ]
    
    async def generate_learning_path(
        self, 
        niche_name: str, 
        answers: Dict[str, str]
    ) -> LearningPathOutput:
        """
        Generate a personalized learning path based on user's niche and question answers
        
        Args:
            niche_name: The name of the niche/industry
            answers: Dictionary mapping question IDs to selected answers
            
        Returns:
            LearningPathOutput containing the personalized learning path
        """
        # Create the system prompt
        system_prompt = """
        You are an expert education curriculum designer with deep expertise in creating personalized learning paths.
        Your task is to design a comprehensive, structured learning journey for a user based on their specific field
        of interest and their answers to personalization questions.
        
        The learning path you create should:
        1. Be tailored to the user's experience level, goals, and preferences
        2. Follow a logical progression from foundational to advanced concepts
        3. Include a diverse mix of high-quality learning resources (courses, books, tutorials, projects)
        4. Provide realistic time estimates for each module
        5. Include practical advice and tips for effective learning
        6. Cover both theoretical knowledge and practical applications
        
        For each module in the learning path:
        - Create a descriptive title
        - Provide a clear explanation of what will be covered
        - List the key topics included
        - Include 3-5 specific, high-quality learning resources with links
        - Assign a difficulty level (Beginner, Intermediate, Advanced)
        - Estimate a realistic timeline for completion
        - Add helpful tips for success in that module
        
        Ensure the entire path is coherent, with later modules building on earlier ones, and the full journey
        addressing all critical aspects of the specified field.
        """
        
        # Format the answers as a readable string
        formatted_answers = "\n".join([f"- {key}: {value}" for key, value in answers.items()])
        
        # Create the user prompt
        user_prompt = f"""
        Please create a personalized learning path for someone interested in the "{niche_name}" field.
        
        ## USER PROFILE:
        Based on their answers to personalization questions:
        {formatted_answers}
        
        Please design a comprehensive learning path that:
        - Is tailored specifically to this user's experience level, goals, and preferences
        - Provides a clear structure from fundamentals to advanced concepts
        - Includes 4-7 well-defined modules that build on each other
        - For each module, includes high-quality, specific learning resources (courses, tutorials, books, etc.)
        - Provides realistic time estimates for completion
        - Includes practical advice and tips throughout
        
        Format the response according to the required schema, with all necessary details for each module and resource.
        """
        
        # Make request to Groq
        try:
            response = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=LearningPathOutput,
                temperature=0.2
            )
            return response
        except Exception as e:
            # Re-raise with more specific context
            raise Exception(f"Learning path generation failed: {str(e)}") 