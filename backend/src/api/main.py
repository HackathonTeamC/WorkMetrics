import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware import error_handler_middleware, logging_middleware
from src.api.routes import api_router
from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create FastAPI application
app = FastAPI(
    title="WorkMetrics API",
    description="GitLab Metrics Dashboard API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middlewares
app.middleware("http")(logging_middleware)
app.middleware("http")(error_handler_middleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "WorkMetrics API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.is_development)
