"""
Baseline Monitor API - Main application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.database import engine, Base

# Import all models to ensure they're registered with SQLAlchemy
from app.modules.users.models import User
from app.modules.rules.models import Rule
from app.modules.agents.models import Agent

# Create all tables (for development - in production use Alembic migrations)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Baseline Monitor API",
    version="1.0.0",
    description="CIS Compliance Monitoring System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Baseline Monitor API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Backend is running!",
        "api_version": "1.0.0"
    }
