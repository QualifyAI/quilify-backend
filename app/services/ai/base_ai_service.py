import instructor
from typing import Optional
from groq import Groq

from app.core.config import settings

class BaseAIService:
    """
    Base class for all AI services providing common functionality
    """
    def __init__(self):
        # Defer initialization to when methods are actually called
        self.groq_client: Optional[Groq] = None
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
    
    async def _make_groq_request(self, system_prompt: str, user_prompt: str, response_model, temperature: float = 0.3):
        """
        Make a request to the Groq API with proper error handling
        
        Args:
            system_prompt: The system prompt to send
            user_prompt: The user prompt to send
            response_model: The Pydantic model to parse the response into
            temperature: The temperature to use for generation (default: 0.3)
            
        Returns:
            The parsed response
        """
        # Ensure client is initialized
        self._ensure_client_initialized()
        
        # Create message list
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=response_model,
                messages=messages,
                temperature=temperature,
                max_tokens=29000  # Increased from 16000 to allow for more detailed responses
            )
            return response
        except Exception as e:
            # Log the error more effectively
            error_msg = f"Error from Groq API: {str(e)}"
            print(error_msg)  # Replace with proper logging
            raise Exception(error_msg) 