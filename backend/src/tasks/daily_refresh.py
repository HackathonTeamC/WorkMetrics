import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.database.session import SessionLocal
from src.models.project import Project
from src.services.data_refresh import DataRefreshService
from src.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="src.tasks.daily_refresh.refresh_all_projects")
def refresh_all_projects() -> dict[str, int]:
    """
    Daily task to refresh data for all projects and calculate metrics.
    
    Returns:
        Summary of refresh operations
    """
    logger.info("Starting daily refresh for all projects")
    
    db = SessionLocal()
    try:
        # Get all projects
        projects = db.query(Project).all()
        
        if not projects:
            logger.info("No projects to refresh")
            return {"projects_processed": 0, "total_deployments": 0}
        
        total_deployments = 0
        projects_processed = 0
        
        for project in projects:
            try:
                # Run async refresh
                result = asyncio.run(_refresh_project_async(project))
                total_deployments += result["deployments"]
                projects_processed += 1
                
                logger.info(
                    f"Refreshed project {project.id} ({project.name}): "
                    f"{result['deployments']} deployments"
                )
                
                # Calculate metrics for last 30 days
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
                
                refresh_service = DataRefreshService(db)
                asyncio.run(
                    refresh_service.calculate_and_save_metrics(project, start_date, end_date)
                )
                
            except Exception as e:
                logger.error(f"Error refreshing project {project.id}: {str(e)}", exc_info=True)
                continue
        
        logger.info(
            f"Daily refresh completed: {projects_processed} projects, "
            f"{total_deployments} total deployments"
        )
        
        return {
            "projects_processed": projects_processed,
            "total_deployments": total_deployments,
        }
        
    except Exception as e:
        logger.error(f"Error in daily refresh task: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


async def _refresh_project_async(project: Project) -> dict[str, int]:
    """Helper to run async refresh for a project."""
    db = SessionLocal()
    try:
        refresh_service = DataRefreshService(db)
        return await refresh_service.refresh_project_data(project, days_back=90)
    finally:
        db.close()


@celery_app.task(name="src.tasks.daily_refresh.refresh_single_project")
def refresh_single_project(project_id: int) -> dict[str, int]:
    """
    Refresh data for a single project (can be called manually or scheduled).
    
    Args:
        project_id: Project ID to refresh
        
    Returns:
        Summary of refresh operation
    """
    logger.info(f"Starting refresh for project {project_id}")
    
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            logger.error(f"Project {project_id} not found")
            return {"error": "Project not found"}
        
        # Run async refresh
        result = asyncio.run(_refresh_project_async(project))
        
        logger.info(
            f"Refresh completed for project {project_id}: {result['deployments']} deployments"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error refreshing project {project_id}: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()
