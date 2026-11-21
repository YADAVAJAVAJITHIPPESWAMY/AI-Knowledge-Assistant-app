"""
FastAPI Main Application
Initializes middleware, registers API routers, and configures database tables.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
# Import all models so Base knows about them for create_all
import app.models

from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.chat import router as chat_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.insights import router as insights_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: initialize tables on startup.
    """
    # Create tables automatically if using SQLite or if migrations haven't run yet
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database initialization notice: {e}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-stack AI Knowledge Assistant with RAG, Vector Search, and Multi-Format Ingestion",
    lifespan=lifespan
)

# CORS Middleware configuration
# Clean origins: exclude wildcard "*" so Starlette never returns a wildcard with allow_credentials=True.
# allow_origin_regex dynamically echoes back the exact requesting origin (Netlify, localhost, etc.)
_cleaned_origins = [o for o in settings.cors_origins if o and o != "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cleaned_origins,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint for container orchestrators and status monitoring."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


# Register v1 routes
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat_router, prefix="/api/chat", tags=["AI Chat & RAG"])
app.include_router(conversations_router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(insights_router, prefix="/api/insights", tags=["Knowledge Insights"])
