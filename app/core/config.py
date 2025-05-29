import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra='ignore')
    
    # Base settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "QualifyAI"
    DEBUG: bool = True
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_NAME: str = os.getenv("MONGODB_NAME", "qualifyai")
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Groq AI settings
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # Apify settings (if needed)
    APIFY_API_KEY: Optional[str] = os.getenv("APIFY_API_KEY")
    
    # Feature flags
    USE_AI_FOR_QUESTIONS: bool = os.getenv("USE_AI_FOR_QUESTIONS", "true").lower() == "true"

settings = Settings()
