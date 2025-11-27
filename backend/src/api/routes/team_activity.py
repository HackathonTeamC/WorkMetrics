from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.models.project import Project
from src.services.activity_analyzer import ActivityAnalyzer

router = APIRouter()


class TeamMemberActivity(BaseModel):
    """Team member activity data."""

    team_member_id: int
    username: str
    name: str
    commit_count: int
    lines_added: int
    lines_deleted: int
    mrs_created: int
    mrs_merged: int
    mrs_closed: int
    reviews_given: int
    review_comments: int
    avg_review_time_hours: float | None


class ReviewLoad(BaseModel):
    """Review load distribution data."""

    team_member_id: int
    username: str
    name: str
    review_count: int
    comment_count: int
    review_load_percentage: float


class TeamActivityResponse(BaseModel):
    """Response model for team activity."""

    period_start: str
    period_end: str
    team_members: list[TeamMemberActivity]
    review_load: list[ReviewLoad]


@router.get(
    "/projects/{project_id}/team-activity", response_model=TeamActivityResponse
)
def get_team_activity(
    project_id: int,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get team activity metrics for a project.
    
    Args:
        project_id: Project ID
        start_date: Start date for analysis
        end_date: End date for analysis
        db: Database session
        
    Returns:
        Team activity metrics including member activity and review load
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

    # Calculate activity metrics
    analyzer = ActivityAnalyzer(db)
    
    # Get team member activity
    activity_metrics = analyzer.calculate_activity_metrics(project_id, start_dt, end_dt)
    
    # Get review load distribution
    review_load = analyzer.get_review_load_distribution(project_id, start_dt, end_dt)

    return {
        "period_start": start_dt.isoformat(),
        "period_end": end_dt.isoformat(),
        "team_members": activity_metrics,
        "review_load": review_load,
    }
