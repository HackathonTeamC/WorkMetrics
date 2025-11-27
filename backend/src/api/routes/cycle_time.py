from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.models.project import Project
from src.services.cycle_time_analyzer import CycleTimeAnalyzer

router = APIRouter()


class StageStats(BaseModel):
    """Statistics for a single stage."""

    name: str
    mean: float
    median: float
    p75: float
    p90: float
    min: float
    max: float


class StageBreakdown(BaseModel):
    """Stage breakdown percentages."""

    coding_percentage: float
    review_percentage: float
    deployment_percentage: float


class CycleTimeMetrics(BaseModel):
    """Cycle time metrics response."""

    count: int
    stages: dict[str, StageStats]
    total: StageStats
    stage_breakdown_avg: StageBreakdown


class CycleTimeDistributionItem(BaseModel):
    """Individual MR cycle time data."""

    mr_id: int
    title: str
    merged_at: str | None
    coding_time: float
    review_time: float
    deployment_time: float
    total_time: float


class CycleTimeResponse(BaseModel):
    """Complete cycle time analysis response."""

    period_start: str
    period_end: str
    metrics: CycleTimeMetrics
    distribution: list[CycleTimeDistributionItem]


@router.get("/projects/{project_id}/cycle-time", response_model=CycleTimeResponse)
def get_cycle_time(
    project_id: int,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get cycle time analysis for a project.
    
    Breaks down cycle time into stages:
    - Coding: Time from first commit to MR creation
    - Review: Time from MR creation to merge
    - Deployment: Time from merge to deployment
    
    Provides percentile statistics (p50, p75, p90) and distribution data.
    
    Args:
        project_id: Project ID
        start_date: Start date for analysis
        end_date: End date for analysis
        db: Database session
        
    Returns:
        Cycle time metrics with stage breakdowns and distribution
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

    # Calculate cycle time metrics
    analyzer = CycleTimeAnalyzer(db)
    
    # Get aggregated metrics
    metrics = analyzer.calculate_cycle_time_metrics(project_id, start_dt, end_dt)
    
    # Get distribution data (limit to top 50 slowest MRs)
    distribution = analyzer.get_cycle_time_distribution(project_id, start_dt, end_dt)
    distribution = distribution[:50]  # Limit for performance

    return {
        "period_start": start_dt.isoformat(),
        "period_end": end_dt.isoformat(),
        "metrics": metrics,
        "distribution": distribution,
    }
