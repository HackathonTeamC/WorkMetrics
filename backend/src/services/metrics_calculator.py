import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.metrics import Deployment, FourKeysMetrics
from src.models.project import Project

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Service for calculating Four Keys DevOps metrics."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_four_keys(
        self, project_id: int, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """
        Calculate Four Keys metrics for a project within a time period.
        
        Args:
            project_id: Project ID
            start_date: Start of period
            end_date: End of period
            
        Returns:
            Dictionary containing all Four Keys metrics
        """
        logger.info(
            f"Calculating Four Keys metrics for project {project_id} "
            f"from {start_date} to {end_date}"
        )

        # Get deployments in the period
        deployments = (
            self.db.execute(
                select(Deployment)
                .where(Deployment.project_id == project_id)
                .where(Deployment.deployed_at >= start_date)
                .where(Deployment.deployed_at <= end_date)
                .order_by(Deployment.deployed_at)
            )
            .scalars()
            .all()
        )

        if not deployments:
            logger.warning(f"No deployments found for project {project_id} in the period")
            return self._empty_metrics(start_date, end_date)

        # Calculate each metric
        deployment_frequency = self._calculate_deployment_frequency(
            deployments, start_date, end_date
        )
        lead_time = self._calculate_lead_time(deployments)
        change_failure_rate = self._calculate_change_failure_rate(deployments)
        time_to_restore = self._calculate_time_to_restore(deployments)

        return {
            "period_start": start_date,
            "period_end": end_date,
            "deployment_frequency": deployment_frequency["frequency"],
            "deployment_count": deployment_frequency["count"],
            "lead_time_hours": lead_time["mean"],
            "lead_time_median_hours": lead_time["median"],
            "change_failure_rate": change_failure_rate["rate"],
            "failed_deployment_count": change_failure_rate["failed_count"],
            "time_to_restore_hours": time_to_restore["mean"],
            "time_to_restore_median_hours": time_to_restore["median"],
        }

    def _empty_metrics(self, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        """Return empty metrics when no deployments exist."""
        return {
            "period_start": start_date,
            "period_end": end_date,
            "deployment_frequency": 0.0,
            "deployment_count": 0,
            "lead_time_hours": None,
            "lead_time_median_hours": None,
            "change_failure_rate": None,
            "failed_deployment_count": 0,
            "time_to_restore_hours": None,
            "time_to_restore_median_hours": None,
        }

    def _calculate_deployment_frequency(
        self, deployments: list[Deployment], start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """
        Calculate deployment frequency (deployments per day).
        
        Metric 1: How often does code get deployed to production?
        """
        deployment_count = len(deployments)
        period_days = max((end_date - start_date).days, 1)
        frequency = deployment_count / period_days

        return {"frequency": frequency, "count": deployment_count}

    def _calculate_lead_time(self, deployments: list[Deployment]) -> dict[str, Any]:
        """
        Calculate lead time for changes (commit to deployment time in hours).
        
        Metric 2: How long does it take to go from code committed to code 
        successfully running in production?
        
        Note: This requires merge request data with first commit time.
        For now, we use the pre-calculated lead_time_hours from deployments.
        """
        lead_times = [d.lead_time_hours for d in deployments if d.lead_time_hours is not None]

        if not lead_times:
            return {"mean": None, "median": None}

        mean = sum(lead_times) / len(lead_times)
        sorted_times = sorted(lead_times)
        n = len(sorted_times)
        median = (
            sorted_times[n // 2]
            if n % 2 == 1
            else (sorted_times[n // 2 - 1] + sorted_times[n // 2]) / 2
        )

        return {"mean": mean, "median": median}

    def _calculate_change_failure_rate(self, deployments: list[Deployment]) -> dict[str, Any]:
        """
        Calculate change failure rate (percentage of deployments causing failure).
        
        Metric 3: What percentage of changes to production result in degraded 
        service and require remediation?
        """
        total_deployments = len(deployments)
        failed_deployments = sum(1 for d in deployments if d.is_failure)

        if total_deployments == 0:
            return {"rate": None, "failed_count": 0}

        rate = (failed_deployments / total_deployments) * 100

        return {"rate": rate, "failed_count": failed_deployments}

    def _calculate_time_to_restore(self, deployments: list[Deployment]) -> dict[str, Any]:
        """
        Calculate time to restore service (hours to recover from failure).
        
        Metric 4: How long does it take to restore service when an incident occurs?
        
        Note: This requires incident detection and resolution timestamps.
        For now, we use the pre-calculated time_to_restore_hours from deployments.
        """
        restore_times = [
            d.time_to_restore_hours for d in deployments if d.time_to_restore_hours is not None
        ]

        if not restore_times:
            return {"mean": None, "median": None}

        mean = sum(restore_times) / len(restore_times)
        sorted_times = sorted(restore_times)
        n = len(sorted_times)
        median = (
            sorted_times[n // 2]
            if n % 2 == 1
            else (sorted_times[n // 2 - 1] + sorted_times[n // 2]) / 2
        )

        return {"mean": mean, "median": median}

    def save_metrics(self, project_id: int, metrics_data: dict[str, Any]) -> FourKeysMetrics:
        """Save calculated metrics to database."""
        metrics = FourKeysMetrics(project_id=project_id, **metrics_data)
        self.db.add(metrics)
        self.db.commit()
        self.db.refresh(metrics)
        logger.info(f"Saved Four Keys metrics for project {project_id}")
        return metrics
