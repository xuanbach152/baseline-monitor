"""
Baseline Monitor API - Main application.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.database import engine, Base, SessionLocal

# Import all models to ensure they're registered with SQLAlchemy
from app.modules.users.models import User
from app.modules.rules.models import Rule
from app.modules.agents.models import Agent
from app.modules.violations.models import Violation

# Create all tables (for development - in production use Alembic migrations)
# Base.metadata.create_all(bind=engine)

# Background task flag
background_task = None


async def check_agent_timeout_loop():
    """
    Background task: Check agent timeouts every 10 seconds.
    Marks stale agents as offline (no heartbeat for 90s) and broadcasts WebSocket events.
    Agent heartbeat interval is 60s, so 90s timeout allows for 1 missed heartbeat.
    """
    from app.modules.agents.utils import mark_stale_agents_offline
    
    while True:
        try:
            db = SessionLocal()
            try:
                count = await mark_stale_agents_offline(db, timeout_minutes=1.5)  # 90 seconds
                if count > 0:
                    print(f" Marked {count} stale agent(s) as offline (timeout: 90s)")
            finally:
                db.close()
        except Exception as e:
            print(f" Error in agent timeout check: {e}")
        
        await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Starts background task when app starts, stops it when app shuts down.
    """
    global background_task
    
    print("Starting agent timeout monitoring (check every 10s, timeout: 30s)...")
    background_task = asyncio.create_task(check_agent_timeout_loop())
    
    yield  
    
    if background_task:
        print("Stopping agent timeout monitoring...")
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Baseline Monitor API",
    version="1.0.0",
    description="CIS Compliance Monitoring System",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
