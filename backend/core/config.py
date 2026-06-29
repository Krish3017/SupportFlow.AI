"""
Core Configuration
Centralized application settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # Application
    APP_NAME: str = "SupportFlow AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "supportflow.db")

    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0"))

    # Email
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "support@yourdomain.com")
    MANAGER_EMAIL: str = os.getenv("MANAGER_EMAIL", "manager@yourdomain.com")

    # Gmail
    GMAIL_CREDENTIALS_PATH: str = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
    GMAIL_TOKEN_PATH: str = os.getenv("GMAIL_TOKEN_PATH", "token.json")
    EMAIL_POLL_INTERVAL_MINUTES: int = int(os.getenv("EMAIL_POLL_INTERVAL_MINUTES", "2"))

    # ChromaDB
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100

    class Config:
        case_sensitive = True

# Global settings instance
settings = Settings()

def validate_required_settings():
    """Validate critical environment variables are set. Called explicitly by main.py."""
    errors = []

    if not settings.GROQ_API_KEY:
        errors.append("GROQ_API_KEY is required")

    if not settings.RESEND_API_KEY:
        errors.append("RESEND_API_KEY is required")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
