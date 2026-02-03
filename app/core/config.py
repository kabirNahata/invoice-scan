from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smart Scan Invoice API"
    
    # Security & API Keys
    GEMINI_API_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/invoices.db"
    
    # Flags
    PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK: bool = True
    FLAGS_use_mkldnn: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
