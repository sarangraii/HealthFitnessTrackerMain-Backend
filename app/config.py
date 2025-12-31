from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/fitness_tracker"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    
    # OpenAI (optional - if you have credits)
    OPENAI_API_KEY: Optional[str] = None
    
    # Google Gemini (FREE - Recommended!)
    GOOGLE_API_KEY: Optional[str] = None
    
    # Groq (FREE - Super Fast!)
    GROQ_API_KEY: Optional[str] = None
    
    # Anthropic Claude (optional)
    ANTHROPIC_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # This allows extra fields in .env without errors

settings = Settings()