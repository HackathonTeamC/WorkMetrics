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
    description="""
## GitLab Metrics Dashboard API

A comprehensive API for analyzing GitLab project metrics and team productivity.

### Features

* **Four Keys Metrics**: DORA DevOps performance indicators
    - Deployment Frequency
    - Lead Time for Changes
    - Change Failure Rate
    - Time to Restore Service

* **Team Activity Analysis**: Individual contributor metrics
    - Commit counts and patterns
    - Merge request activity
    - Code review load distribution
    - Team member productivity insights

* **Cycle Time Analysis**: Process bottleneck identification
    - Stage-based breakdown (coding, review, deployment)
    - Percentile statistics (p50, p75, p90)
    - Distribution visualization
    - Automated bottleneck detection

### Data Sources

This API integrates with GitLab API to collect and analyze:
- Project information
- Deployments
- Merge requests and commits
- Issues and milestones
- Team member activity

### Authentication

Currently uses GitLab Personal Access Token configured via environment variables.
Future versions will support OAuth2 authentication.

### Rate Limiting

API calls to GitLab are rate-limited to 60 requests per minute by default.
This can be configured via `GITLAB_API_RATE_LIMIT_PER_MINUTE` environment variable.

### Caching

Historical data is cached for 24 hours, while recent data is cached for 1 hour
to balance freshness with API quota usage.

### Refresh Strategy

Data is automatically refreshed daily at 2:00 AM (configurable).
Manual refresh can be triggered via the `/projects/{id}/refresh` endpoint.
    """,
    version="0.1.0",
    contact={
        "name": "WorkMetrics Team",
        "url": "https://github.com/HackathonTeamC/WorkMetrics",
        "email": "support@workmetrics.example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check and service status endpoints",
        },
        {
            "name": "projects",
            "description": "Project management operations (CRUD, refresh)",
        },
        {
            "name": "metrics",
            "description": "Four Keys DevOps performance metrics",
        },
        {
            "name": "team-activity",
            "description": "Team member activity and review load analysis",
        },
        {
            "name": "cycle-time",
            "description": "Cycle time analysis with stage breakdowns",
        },
    ],
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
