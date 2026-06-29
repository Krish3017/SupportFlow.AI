"""
SupportFlow AI - FastAPI Backend
Multi-agent customer support platform powered by LangGraph and Groq
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_tables
from agents.email_agent import EmailAgent
from core.config import settings, validate_required_settings
from core.logging_config import setup_logging, get_logger

# Feature modules
from apps.chat import router as chat_router
from apps.tickets import router as tickets_router
from apps.conversations import router as conversations_router
from apps.customers import router as customers_router
from apps.observatory import router as observatory_router
from apps.knowledge import router as knowledge_router
from apps.analytics import router as analytics_router
from apps.activity import router as activity_router
from apps.email import router as email_router

# Setup logging
setup_logging(level=settings.LOG_LEVEL)
logger = get_logger(__name__)

create_tables()
validate_required_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-agent customer support platform API",
    version=settings.APP_VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (feature-based)
app.include_router(chat_router)
app.include_router(tickets_router)
app.include_router(conversations_router)
app.include_router(customers_router)
app.include_router(observatory_router)
app.include_router(knowledge_router)
app.include_router(analytics_router)
app.include_router(activity_router)
app.include_router(email_router)


# ── Email Agent Lifecycle ─────────────────────────────────────────────────────
@app.on_event("startup")
async def start_email_agent():
    """
    Start the Email Agent as a background task when FastAPI boots.
    It runs alongside the API — no separate process needed.
    """
    from apps.chat.router import workflow
    email_agent = EmailAgent(workflow=workflow)
    asyncio.create_task(email_agent.run())
    logger.info("📧 Email Agent background task started.")


# ── Health Check Endpoints ────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "status":  "online",
        "service": "SupportFlow AI",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status":  "healthy",
        "groq_api_configured":   bool(os.getenv("GROQ_API_KEY")),
        "resend_api_configured": bool(os.getenv("RESEND_API_KEY")),
        "endpoints": {
            "chat":  "/api/chat",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "True").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info")
    )