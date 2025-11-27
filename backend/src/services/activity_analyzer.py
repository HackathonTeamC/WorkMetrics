import logging
from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.team_member import ActivityMetrics, MergeRequest, Review, TeamMember

logger = logging.getLogger(__name__)


class ActivityAnalyzer:
    """Service for analyzing team member activity and calculating metrics."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_activity_metrics(
        self, project_id: int, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        """
        Calculate activity metrics for all team members in a project.
        
        Args:
            project_id: Project ID
            start_date: Start of analysis period
            end_date: End of analysis period
            
        Returns:
            List of activity metrics per team member
        """
        team_members = (
            self.db.query(TeamMember).filter(TeamMember.project_id == project_id).all()
        )

        metrics_list = []
        for member in team_members:
            metrics = self._calculate_member_metrics(member.id, start_date, end_date)
            metrics_list.append(
                {
                    "team_member_id": member.id,
                    "username": member.username,
                    "name": member.name,
                    **metrics,
                }
            )

        return metrics_list

    def _calculate_member_metrics(
        self, team_member_id: int, start_date: datetime, end_date: datetime
    ) -> dict:
        """Calculate metrics for a single team member."""
        # Get merge requests created by this member
        mrs = (
            self.db.query(MergeRequest)
            .filter(
                MergeRequest.author_id == team_member_id,
                MergeRequest.created_at_gitlab >= start_date,
                MergeRequest.created_at_gitlab <= end_date,
            )
            .all()
        )

        # Calculate MR statistics
        mrs_created = len(mrs)
        mrs_merged = sum(1 for mr in mrs if mr.state == "merged")
        mrs_closed = sum(1 for mr in mrs if mr.state == "closed" and not mr.merged_at)
        lines_added = sum(mr.additions for mr in mrs)
        lines_deleted = sum(mr.deletions for mr in mrs)

        # Get reviews given by this member
        reviews = (
            self.db.query(Review)
            .filter(
                Review.reviewer_id == team_member_id,
                Review.reviewed_at >= start_date,
                Review.reviewed_at <= end_date,
            )
            .all()
        )

        reviews_given = len(reviews)
        review_comments = sum(review.comment_count for review in reviews)

        # Calculate average review time (time from MR creation to first review)
        avg_review_time_hours = self._calculate_avg_review_time(reviews)

        # For now, we'll estimate commit count based on MRs
        # In a real implementation, this would fetch from GitLab API
        commit_count = mrs_created * 3  # Rough estimate

        return {
            "commit_count": commit_count,
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "mrs_created": mrs_created,
            "mrs_merged": mrs_merged,
            "mrs_closed": mrs_closed,
            "reviews_given": reviews_given,
            "review_comments": review_comments,
            "avg_review_time_hours": avg_review_time_hours,
        }

    def _calculate_avg_review_time(self, reviews: list[Review]) -> float | None:
        """Calculate average time from MR creation to review."""
        if not reviews:
            return None

        review_times = []
        for review in reviews:
            mr = review.merge_request
            if mr and mr.created_at_gitlab:
                time_diff = review.reviewed_at - mr.created_at_gitlab
                review_times.append(time_diff.total_seconds() / 3600)  # Convert to hours

        if not review_times:
            return None

        return sum(review_times) / len(review_times)

    def get_review_load_distribution(
        self, project_id: int, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        """
        Calculate review load distribution across team members.
        
        Args:
            project_id: Project ID
            start_date: Start of analysis period
            end_date: End of analysis period
            
        Returns:
            List of review load per team member
        """
        # Query reviews grouped by reviewer
        review_counts = (
            self.db.query(
                TeamMember.id,
                TeamMember.username,
                TeamMember.name,
                func.count(Review.id).label("review_count"),
                func.sum(Review.comment_count).label("total_comments"),
            )
            .join(Review, Review.reviewer_id == TeamMember.id)
            .filter(
                TeamMember.project_id == project_id,
                Review.reviewed_at >= start_date,
                Review.reviewed_at <= end_date,
            )
            .group_by(TeamMember.id, TeamMember.username, TeamMember.name)
            .all()
        )

        # Calculate total reviews for percentage
        total_reviews = sum(row.review_count for row in review_counts)

        result = []
        for row in review_counts:
            percentage = (
                (row.review_count / total_reviews * 100) if total_reviews > 0 else 0
            )
            result.append(
                {
                    "team_member_id": row.id,
                    "username": row.username,
                    "name": row.name,
                    "review_count": row.review_count,
                    "comment_count": row.total_comments or 0,
                    "review_load_percentage": round(percentage, 2),
                }
            )

        # Sort by review count descending
        result.sort(key=lambda x: x["review_count"], reverse=True)

        return result

    def save_activity_metrics(
        self, team_member_id: int, start_date: datetime, end_date: datetime, metrics: dict
    ) -> ActivityMetrics:
        """Save calculated activity metrics to database."""
        # Check if metrics already exist for this period
        existing = (
            self.db.query(ActivityMetrics)
            .filter(
                ActivityMetrics.team_member_id == team_member_id,
                ActivityMetrics.period_start == start_date,
                ActivityMetrics.period_end == end_date,
            )
            .first()
        )

        if existing:
            # Update existing metrics
            for key, value in metrics.items():
                setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new metrics
            activity_metrics = ActivityMetrics(
                team_member_id=team_member_id,
                period_start=start_date,
                period_end=end_date,
                **metrics,
            )
            self.db.add(activity_metrics)
            self.db.commit()
            self.db.refresh(activity_metrics)
            return activity_metrics
