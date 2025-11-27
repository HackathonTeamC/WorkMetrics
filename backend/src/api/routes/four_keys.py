from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.models.project import Project
from src.services.metrics_calculator import MetricsCalculator

router = APIRouter()


class FourKeysMetricsResponse(BaseModel):
    """Response model for Four Keys metrics."""

    period_start: str
    period_end: str
    deployment_frequency: float
    deployment_count: int
    lead_time_hours: float | None
    lead_time_median_hours: float | None
    change_failure_rate: float | None
    failed_deployment_count: int
    time_to_restore_hours: float | None
    time_to_restore_median_hours: float | None


@router.get(
    "/projects/{project_id}/four-keys", response_model=FourKeysMetricsResponse
)
def get_four_keys_metrics(
    project_id: int,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Get Four Keys DevOps metrics for a project.
    
    Args:
        project_id: Project ID
        start_date: Start date for metrics calculation
        end_date: End date for metrics calculation
        db: Database session
        
    Returns:
        Four Keys metrics for the specified period
    """
    # Validate project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )

    # Parse dates
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        # Set end time to end of day
        end_dt = end_dt.replace(hour=23, minute=59, second=59)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}. Use YYYY-MM-DD",
        )

    # Validate date range
    if start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="start_date must be before end_date"
        )

    # Calculate metrics
    calculator = MetricsCalculator(db)
    metrics = calculator.calculate_four_keys(project_id, start_dt, end_dt)

    # Format response
    return {
        "period_start": metrics["period_start"].isoformat(),
        "period_end": metrics["period_end"].isoformat(),
        "deployment_frequency": metrics["deployment_frequency"],
        "deployment_count": metrics["deployment_count"],
        "lead_time_hours": metrics["lead_time_hours"],
        "lead_time_median_hours": metrics["lead_time_median_hours"],
        "change_failure_rate": metrics["change_failure_rate"],
        "failed_deployment_count": metrics["failed_deployment_count"],
        "time_to_restore_hours": metrics["time_to_restore_hours"],
        "time_to_restore_median_hours": metrics["time_to_restore_median_hours"],
    }
