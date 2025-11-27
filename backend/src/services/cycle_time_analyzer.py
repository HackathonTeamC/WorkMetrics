import logging
from datetime import datetime, timedelta
from typing import Any

import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.metrics import Deployment
from src.models.team_member import MergeRequest

logger = logging.getLogger(__name__)


class CycleTimeAnalyzer:
    """Service for analyzing cycle time and stage breakdowns."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_cycle_time_metrics(
        self, project_id: int, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """
        Calculate cycle time metrics broken down by stages.
        
        Stages:
        - Coding: Time from first commit to MR creation
        - Review: Time from MR creation to merge
        - Deployment: Time from merge to deployment
        
        Args:
            project_id: Project ID
            start_date: Start of analysis period
            end_date: End of analysis period
            
        Returns:
            Cycle time metrics with stage breakdowns and percentiles
        """
        logger.info(
            f"Calculating cycle time metrics for project {project_id} "
            f"from {start_date} to {end_date}"
        )

        # Get merged MRs in the period
        merged_mrs = (
            self.db.query(MergeRequest)
            .filter(
                MergeRequest.project_id == project_id,
                MergeRequest.state == "merged",
                MergeRequest.merged_at >= start_date,
                MergeRequest.merged_at <= end_date,
            )
            .all()
        )

        if not merged_mrs:
            return self._empty_metrics()

        # Calculate stage times for each MR
        stage_times = []
        for mr in merged_mrs:
            stage_data = self._calculate_mr_stage_times(mr)
            if stage_data:
                stage_times.append(stage_data)

        if not stage_times:
            return self._empty_metrics()

        # Calculate aggregated metrics
        metrics = self._aggregate_stage_metrics(stage_times)
        
        logger.info(f"Calculated cycle time metrics for {len(stage_times)} MRs")
        return metrics

    def _calculate_mr_stage_times(self, mr: MergeRequest) -> dict[str, float] | None:
        """
        Calculate stage times for a single MR.
        
        Returns:
            Dictionary with stage times in hours, or None if data is incomplete
        """
        if not mr.created_at_gitlab or not mr.merged_at:
            return None

        # Review time: MR creation to merge
        review_time = (mr.merged_at - mr.created_at_gitlab).total_seconds() / 3600

        # For now, estimate coding time as 24h before MR creation
        # In a real implementation, this would use commit timestamps
        coding_time = 24.0  # Default estimate

        # Deployment time: Try to find deployment after merge
        deployment = (
            self.db.query(Deployment)
            .filter(
                Deployment.project_id == mr.project_id,
                Deployment.deployed_at >= mr.merged_at,
                Deployment.deployed_at <= mr.merged_at + timedelta(days=7),
            )
            .order_by(Deployment.deployed_at)
            .first()
        )

        if deployment and deployment.deployed_at:
            deployment_time = (
                deployment.deployed_at - mr.merged_at
            ).total_seconds() / 3600
        else:
            # If no deployment found, use default
            deployment_time = 0.5  # 30 minutes default

        # Total cycle time
        total_time = coding_time + review_time + deployment_time

        return {
            "coding_time": coding_time,
            "review_time": review_time,
            "deployment_time": deployment_time,
            "total_time": total_time,
        }

    def _aggregate_stage_metrics(self, stage_times: list[dict]) -> dict[str, Any]:
        """
        Aggregate stage times and calculate percentiles.
        
        Args:
            stage_times: List of stage time dictionaries
            
        Returns:
            Aggregated metrics with percentiles
        """
        # Extract arrays for each stage
        coding_times = [st["coding_time"] for st in stage_times]
        review_times = [st["review_time"] for st in stage_times]
        deployment_times = [st["deployment_time"] for st in stage_times]
        total_times = [st["total_time"] for st in stage_times]

        return {
            "count": len(stage_times),
            "stages": {
                "coding": self._calculate_stage_stats(coding_times, "Coding"),
                "review": self._calculate_stage_stats(review_times, "Review"),
                "deployment": self._calculate_stage_stats(deployment_times, "Deployment"),
            },
            "total": self._calculate_stage_stats(total_times, "Total"),
            "stage_breakdown_avg": {
                "coding_percentage": (
                    np.mean(coding_times) / np.mean(total_times) * 100
                    if total_times
                    else 0
                ),
                "review_percentage": (
                    np.mean(review_times) / np.mean(total_times) * 100
                    if total_times
                    else 0
                ),
                "deployment_percentage": (
                    np.mean(deployment_times) / np.mean(total_times) * 100
                    if total_times
                    else 0
                ),
            },
        }

    def _calculate_stage_stats(
        self, times: list[float], stage_name: str
    ) -> dict[str, Any]:
        """
        Calculate statistics for a single stage.
        
        Args:
            times: List of time values in hours
            stage_name: Name of the stage
            
        Returns:
            Statistics dictionary
        """
        if not times:
            return {
                "name": stage_name,
                "mean": 0,
                "median": 0,
                "p75": 0,
                "p90": 0,
                "min": 0,
                "max": 0,
            }

        times_array = np.array(times)
        
        return {
            "name": stage_name,
            "mean": float(np.mean(times_array)),
            "median": float(np.median(times_array)),
            "p75": float(np.percentile(times_array, 75)),
            "p90": float(np.percentile(times_array, 90)),
            "min": float(np.min(times_array)),
            "max": float(np.max(times_array)),
        }

    def _empty_metrics(self) -> dict[str, Any]:
        """Return empty metrics structure."""
        return {
            "count": 0,
            "stages": {
                "coding": self._calculate_stage_stats([], "Coding"),
                "review": self._calculate_stage_stats([], "Review"),
                "deployment": self._calculate_stage_stats([], "Deployment"),
            },
            "total": self._calculate_stage_stats([], "Total"),
            "stage_breakdown_avg": {
                "coding_percentage": 0,
                "review_percentage": 0,
                "deployment_percentage": 0,
            },
        }

    def get_cycle_time_distribution(
        self, project_id: int, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        """
        Get cycle time distribution data for visualization.
        
        Args:
            project_id: Project ID
            start_date: Start of analysis period
            end_date: End of analysis period
            
        Returns:
            List of data points for distribution chart
        """
        merged_mrs = (
            self.db.query(MergeRequest)
            .filter(
                MergeRequest.project_id == project_id,
                MergeRequest.state == "merged",
                MergeRequest.merged_at >= start_date,
                MergeRequest.merged_at <= end_date,
            )
            .all()
        )

        distribution = []
        for mr in merged_mrs:
            stage_data = self._calculate_mr_stage_times(mr)
            if stage_data:
                distribution.append(
                    {
                        "mr_id": mr.gitlab_mr_iid,
                        "title": mr.title,
                        "merged_at": mr.merged_at.isoformat() if mr.merged_at else None,
                        **stage_data,
                    }
                )

        # Sort by total time descending
        distribution.sort(key=lambda x: x["total_time"], reverse=True)
        
        return distribution
