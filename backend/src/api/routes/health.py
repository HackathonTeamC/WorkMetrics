from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database.session import get_db

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Health check endpoint.
    
    Verifies that the API is running and can connect to the database.
    
    Returns:
        Health status information
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "service": "workmetrics-api",
    }
