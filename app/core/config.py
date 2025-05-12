import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
