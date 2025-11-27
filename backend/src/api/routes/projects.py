from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.models.project import Project
from src.services.data_refresh import DataRefreshService

router = APIRouter()


class CreateProjectRequest(BaseModel):
    """Request model for creating a project."""

    gitlab_id: int
    name: str
    url: str


class ProjectResponse(BaseModel):
    """Response model for project."""

    id: int
    gitlab_id: int
    name: str
    url: str
    last_synced_at: str | None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class RefreshResponse(BaseModel):
    """Response model for data refresh."""

    message: str
    deployments_count: int


@router.post("/projects", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
def create_project(
    request: CreateProjectRequest, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """
    Create a new GitLab project.
    
    Args:
        request: Project creation request
        db: Database session
        
    Returns:
        Created project
    """
    # Check if project already exists
    existing = db.query(Project).filter(Project.gitlab_id == request.gitlab_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with GitLab ID {request.gitlab_id} already exists",
        )

    # Create project
    project = Project(
        gitlab_id=request.gitlab_id, name=request.name, url=request.url, last_synced_at=None
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)) -> list[Project]:
    """
    List all projects.
    
    Args:
        db: Database session
        
    Returns:
        List of projects
    """
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return projects


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)) -> Project:
    """
    Get a specific project.
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        Project details
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )

    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)) -> None:
    """
    Delete a project.
    
    Args:
        project_id: Project ID
        db: Database session
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )

    db.delete(project)
    db.commit()


@router.post("/projects/{project_id}/refresh", response_model=RefreshResponse)
async def refresh_project(project_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Manually trigger data refresh for a project.
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        Refresh results
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )

    # Refresh data
    refresh_service = DataRefreshService(db)
    try:
        result = await refresh_service.refresh_project_data(project, days_back=90)
        return {
            "message": f"Data refresh completed for project {project.name}",
            "deployments_count": result["deployments"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh data: {str(e)}",
        )
