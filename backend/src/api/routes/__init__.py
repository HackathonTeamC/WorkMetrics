from fastapi import APIRouter

from src.api.routes.four_keys import router as four_keys_router
from src.api.routes.health import router as health_router
from src.api.routes.projects import router as projects_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, tags=["health"])
api_router.include_router(projects_router, tags=["projects"])
api_router.include_router(four_keys_router, tags=["metrics"])

__all__ = ["api_router"]
