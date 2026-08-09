"""
Core Configuration
Centralized application settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

def parse_cors_origins() -> List[str]:
    raw = os.getenv("CORS_ORIGINS", "")
    origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://support-flow-ai-liard.vercel.app"
    ]
    if raw:
        if raw.strip().startswith("[") and raw.strip().endswith("]"):
            try:
                import json
                parsed = json.loads(raw)
                for item in parsed:
                    clean = str(item).strip().strip("'").strip('"').rstrip("/")
                    if clean and clean not in origins:
                        origins.append(clean)
            except Exception:
                pass
        for item in raw.split(","):
            clean = item.strip().strip("'").strip('"').rstrip("/")
            if clean and clean not in origins:
                origins.append(clean)
    return origins


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # Application
    APP_NAME: str = "SupportFlow AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    # CORS & Cookies
    CORS_ORIGINS: List[str] = parse_cors_origins()

    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "False").lower() == "true" or os.getenv("ENVIRONMENT", "development").lower() == "production"
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "lax" if os.getenv("ENVIRONMENT", "development").lower() != "production" else "none")

    # Security & Admin Auth
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_SESSION_SECRET: str = os.getenv("ADMIN_SESSION_SECRET", "super-secret-admin-session-key-change-in-prod")

    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "supportflow.db")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

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

    if settings.ENVIRONMENT.lower() == "production":
        if not settings.DATABASE_URL:
            errors.append("DATABASE_URL is required in production environment")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

