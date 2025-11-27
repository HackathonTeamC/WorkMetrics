from fastapi import APIRouter

from src.api.routes.health import router as health_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, tags=["health"])

__all__ = ["api_router"]
