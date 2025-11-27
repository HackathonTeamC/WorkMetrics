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

    async def refresh_team_activity_data(
        self, project: Project, days_back: int = 90
    ) -> dict[str, int]:
        """
        Refresh team activity data (MRs, reviews, team members) from GitLab.
        
        Args:
            project: Project to refresh
            days_back: Number of days to fetch historical data
            
        Returns:
            Dictionary with counts of updated records
        """
        from src.models.team_member import MergeRequest, Review, TeamMember

        logger.info(
            f"Starting team activity data refresh for project {project.id} ({project.name})"
        )

        try:
            # Fetch merge requests from GitLab
            mrs_data = await self._fetch_merge_requests(project, days_back)
            
            # Process merge requests and team members
            team_members_map = {}
            saved_mrs = 0
            
            for mr_data in mrs_data:
                # Get or create author
                author = self._get_or_create_team_member(
                    project, mr_data["author"], team_members_map
                )
                
                # Process merge request
                mr = self._process_merge_request(project, author, mr_data)
                if mr:
                    saved_mrs += 1
                    
                    # Fetch and process reviews for this MR
                    await self._fetch_and_process_reviews(project, mr, team_members_map)
            
            self.db.commit()
            
            logger.info(
                f"Team activity data refresh completed for project {project.id}: "
                f"{saved_mrs} MRs, {len(team_members_map)} team members"
            )
            
            return {
                "merge_requests": saved_mrs,
                "team_members": len(team_members_map),
            }
            
        except Exception as e:
            logger.error(
                f"Error refreshing team activity for project {project.id}: {str(e)}",
                exc_info=True,
            )
            self.db.rollback()
            raise

    async def _fetch_merge_requests(
        self, project: Project, days_back: int
    ) -> list[dict]:
        """Fetch merge requests from GitLab API."""
        logger.debug(f"Fetching merge requests for GitLab project {project.gitlab_id}")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Fetch from GitLab
        params = {
            "updated_after": start_date.isoformat(),
            "per_page": 100,
            "order_by": "updated_at",
            "sort": "desc",
        }
        
        mrs = await self.gitlab_client.get_project_merge_requests(
            project.gitlab_id, params=params
        )
        
        logger.debug(f"Fetched {len(mrs)} merge requests from GitLab")
        return mrs

    def _get_or_create_team_member(
        self, project: Project, user_data: dict, members_map: dict
    ) -> "TeamMember":
        """Get or create a team member record."""
        from src.models.team_member import TeamMember

        gitlab_user_id = user_data["id"]
        
        # Check cache first
        if gitlab_user_id in members_map:
            return members_map[gitlab_user_id]
        
        # Check database
        member = (
            self.db.query(TeamMember)
            .filter(
                TeamMember.project_id == project.id,
                TeamMember.gitlab_user_id == gitlab_user_id,
            )
            .first()
        )
        
        if not member:
            # Create new team member
            member = TeamMember(
                project_id=project.id,
                gitlab_user_id=gitlab_user_id,
                username=user_data.get("username", ""),
                name=user_data.get("name", ""),
                email=user_data.get("email"),
                avatar_url=user_data.get("avatar_url"),
            )
            self.db.add(member)
            self.db.flush()  # Get ID without committing
            logger.debug(f"Created team member {member.username}")
        
        members_map[gitlab_user_id] = member
        return member

    def _process_merge_request(
        self, project: Project, author: "TeamMember", mr_data: dict
    ) -> "MergeRequest | None":
        """Process and save merge request record."""
        from src.models.team_member import MergeRequest

        try:
            # Check if MR already exists
            existing = (
                self.db.query(MergeRequest)
                .filter(
                    MergeRequest.project_id == project.id,
                    MergeRequest.gitlab_mr_id == mr_data["id"],
                )
                .first()
            )
            
            if existing:
                # Update existing MR
                existing.state = mr_data.get("state", existing.state)
                existing.merged_at = self._parse_datetime(mr_data.get("merged_at"))
                existing.closed_at = self._parse_datetime(mr_data.get("closed_at"))
                existing.additions = mr_data.get("changes", {}).get("additions", 0)
                existing.deletions = mr_data.get("changes", {}).get("deletions", 0)
                return existing
            else:
                # Create new MR
                mr = MergeRequest(
                    project_id=project.id,
                    author_id=author.id,
                    gitlab_mr_id=mr_data["id"],
                    gitlab_mr_iid=mr_data["iid"],
                    title=mr_data["title"],
                    state=mr_data.get("state", "opened"),
                    created_at_gitlab=self._parse_datetime(mr_data["created_at"]),
                    merged_at=self._parse_datetime(mr_data.get("merged_at")),
                    closed_at=self._parse_datetime(mr_data.get("closed_at")),
                    source_branch=mr_data.get("source_branch", ""),
                    target_branch=mr_data.get("target_branch", ""),
                    additions=mr_data.get("changes", {}).get("additions", 0),
                    deletions=mr_data.get("changes", {}).get("deletions", 0),
                )
                self.db.add(mr)
                self.db.flush()  # Get ID
                logger.debug(f"Created merge request {mr.gitlab_mr_iid}")
                return mr
                
        except Exception as e:
            logger.error(f"Error processing MR {mr_data.get('iid')}: {str(e)}")
            return None

    async def _fetch_and_process_reviews(
        self, project: Project, mr: "MergeRequest", members_map: dict
    ) -> None:
        """Fetch and process reviews for a merge request."""
        from src.models.team_member import Review

        # For simplicity, we'll simulate review data
        # In a real implementation, this would fetch from GitLab API
        # (notes/comments on the MR)
        
        # This is a placeholder - GitLab API doesn't have a direct "reviews" endpoint
        # You'd need to fetch MR notes/comments and parse them
        pass

    async def calculate_and_cache_cycle_time(
        self, project: Project, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """
        Calculate cycle time metrics for a project and period.
        
        Note: Cycle time is calculated on-demand from MR data,
        so no special data fetching is needed. This method is
        provided for consistency with other metric calculations.
        
        Args:
            project: Project to analyze
            start_date: Start of analysis period
            end_date: End of analysis period
            
        Returns:
            Cycle time metrics
        """
        from src.services.cycle_time_analyzer import CycleTimeAnalyzer

        logger.info(
            f"Calculating cycle time metrics for project {project.id} "
            f"from {start_date} to {end_date}"
        )

        analyzer = CycleTimeAnalyzer(self.db)
        metrics = analyzer.calculate_cycle_time_metrics(project.id, start_date, end_date)

        logger.info(f"Cycle time metrics calculated for project {project.id}")
        return metrics
