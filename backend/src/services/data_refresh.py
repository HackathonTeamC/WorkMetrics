import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.models.metrics import Deployment
from src.models.project import Project
from src.services.gitlab_client import GitLabClient
from src.services.metrics_calculator import MetricsCalculator

logger = logging.getLogger(__name__)


class DataRefreshService:
    """Service for orchestrating data refresh from GitLab and metrics calculation."""

    def __init__(self, db: Session, gitlab_client: GitLabClient | None = None):
        self.db = db
        self.gitlab_client = gitlab_client or GitLabClient()
        self.metrics_calculator = MetricsCalculator(db)

    async def refresh_project_data(
        self, project: Project, days_back: int = 90
    ) -> dict[str, int]:
        """
        Refresh data for a project from GitLab.
        
        Args:
            project: Project to refresh
            days_back: Number of days to fetch historical data
            
        Returns:
            Dictionary with counts of updated records
        """
        logger.info(f"Starting data refresh for project {project.id} ({project.name})")

        try:
            # Fetch deployments from GitLab
            deployments_data = await self._fetch_deployments(project, days_back)
            
            # Process and save deployments
            saved_count = self._process_deployments(project, deployments_data)
            
            # Update last_synced_at
            project.last_synced_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(
                f"Data refresh completed for project {project.id}: "
                f"{saved_count} deployments processed"
            )
            
            return {"deployments": saved_count}
            
        except Exception as e:
            logger.error(f"Error refreshing project {project.id}: {str(e)}", exc_info=True)
            self.db.rollback()
            raise

    async def _fetch_deployments(self, project: Project, days_back: int) -> list[dict]:
        """Fetch deployments from GitLab API."""
        logger.debug(f"Fetching deployments for GitLab project {project.gitlab_id}")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Fetch from GitLab
        params = {
            "updated_after": start_date.isoformat(),
            "updated_before": end_date.isoformat(),
            "per_page": 100,
        }
        
        deployments = await self.gitlab_client.get_project_deployments(
            project.gitlab_id, params=params
        )
        
        logger.debug(f"Fetched {len(deployments)} deployments from GitLab")
        return deployments

    def _process_deployments(self, project: Project, deployments_data: list[dict]) -> int:
        """Process and save deployment records."""
        saved_count = 0
        
        for deployment_data in deployments_data:
            try:
                # Check if deployment already exists
                existing = (
                    self.db.query(Deployment)
                    .filter(
                        Deployment.project_id == project.id,
                        Deployment.gitlab_deployment_id == deployment_data["id"],
                    )
                    .first()
                )
                
                if existing:
                    # Update existing deployment
                    self._update_deployment(existing, deployment_data)
                else:
                    # Create new deployment
                    self._create_deployment(project, deployment_data)
                
                saved_count += 1
                
            except Exception as e:
                logger.error(
                    f"Error processing deployment {deployment_data.get('id')}: {str(e)}"
                )
                continue
        
        self.db.commit()
        return saved_count

    def _create_deployment(self, project: Project, data: dict) -> Deployment:
        """Create a new deployment record."""
        deployment = Deployment(
            project_id=project.id,
            gitlab_deployment_id=data["id"],
            environment=data.get("environment", {}).get("name", "unknown"),
            status=data.get("status", "unknown"),
            deployed_at=self._parse_datetime(data.get("created_at")),
            finished_at=self._parse_datetime(data.get("updated_at")),
            commit_sha=data.get("sha", "")[:40],
            merge_request_iid=None,  # Would need to fetch from commit
            is_failure=data.get("status") in ["failed", "canceled"],
        )
        
        self.db.add(deployment)
        logger.debug(f"Created deployment {deployment.gitlab_deployment_id}")
        return deployment

    def _update_deployment(self, deployment: Deployment, data: dict) -> None:
        """Update an existing deployment record."""
        deployment.status = data.get("status", deployment.status)
        deployment.finished_at = self._parse_datetime(data.get("updated_at"))
        deployment.is_failure = data.get("status") in ["failed", "canceled"]
        
        logger.debug(f"Updated deployment {deployment.gitlab_deployment_id}")

    def _parse_datetime(self, date_str: str | None) -> datetime | None:
        """Parse ISO datetime string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    async def calculate_and_save_metrics(
        self, project: Project, start_date: datetime, end_date: datetime
    ) -> None:
        """Calculate and save Four Keys metrics for a project and period."""
        logger.info(
            f"Calculating metrics for project {project.id} "
            f"from {start_date} to {end_date}"
        )
        
        # Calculate metrics
        metrics_data = self.metrics_calculator.calculate_four_keys(
            project.id, start_date, end_date
        )
        
        # Save to database
        self.metrics_calculator.save_metrics(project.id, metrics_data)
        
        logger.info(f"Metrics calculated and saved for project {project.id}")
