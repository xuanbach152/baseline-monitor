"""API v1 router aggregation."""
from fastapi import APIRouter

from app.modules.users.router import router as users_router
from app.modules.rules.router import router as rules_router
from app.modules.agents.router import router as agents_router
from app.modules.violations.router import router as violations_router

api_router = APIRouter(prefix="/api/v1")

# Include all module routers
api_router.include_router(users_router)
api_router.include_router(rules_router)
api_router.include_router(agents_router)
api_router.include_router(violations_router)
