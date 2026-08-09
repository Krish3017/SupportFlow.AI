import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings, validate_required_settings
from core.logging_config import setup_logging, get_logger

from apps.chat import router as chat_router
from apps.tickets import router as tickets_router
from apps.conversations import router as conversations_router
from apps.customers import router as customers_router
from apps.observatory import router as observatory_router
from apps.knowledge import router as knowledge_router
from apps.analytics import router as analytics_router
from apps.activity import router as activity_router
from apps.email import router as email_router
from apps.auth import router as auth_router

from contextlib import asynccontextmanager
from core.postgres import init_postgres_pool, close_postgres_pool

setup_logging(level=settings.LOG_LEVEL)
logger = get_logger(__name__)

validate_required_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing application resources...")
    init_postgres_pool()
    yield
    logger.info("Shutting down application resources...")
    close_postgres_pool()


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-native customer support platform API",
    version=settings.APP_VERSION,
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(tickets_router)
app.include_router(conversations_router)
app.include_router(customers_router)
app.include_router(observatory_router)
app.include_router(knowledge_router)
app.include_router(analytics_router)
app.include_router(activity_router)
app.include_router(email_router)




@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "SupportFlow AI",
        "version": settings.APP_VERSION
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "groq_api_configured": bool(os.getenv("GROQ_API_KEY")),
        "resend_api_configured": bool(os.getenv("RESEND_API_KEY")),
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
