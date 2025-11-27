from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseModel

if TYPE_CHECKING:
    from src.models.project import Project


class FourKeysMetrics(BaseModel):
    """Four Keys metrics for a specific time period."""

    __tablename__ = "four_keys_metrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Time period
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Four Keys Metrics
    # 1. Deployment Frequency (deployments per day)
    deployment_frequency: Mapped[float] = mapped_column(Float, nullable=False)
    deployment_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    # 2. Lead Time for Changes (hours)
    lead_time_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    lead_time_median_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # 3. Change Failure Rate (percentage)
    change_failure_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    failed_deployment_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    
    # 4. Time to Restore Service (hours)
    time_to_restore_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_to_restore_median_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="four_keys_metrics")

    def __repr__(self) -> str:
        return (
            f"<FourKeysMetrics(id={self.id}, project_id={self.project_id}, "
            f"period={self.period_start.date()}-{self.period_end.date()})>"
        )


class Deployment(BaseModel):
    """GitLab deployment record."""

    __tablename__ = "deployments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # GitLab deployment info
    gitlab_deployment_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    environment: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # success, failed, canceled, etc.
    
    # Timestamps
    deployed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Related commit/MR info
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    merge_request_iid: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    
    # Metrics calculation fields
    is_failure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    lead_time_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_to_restore_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="deployments")

    def __repr__(self) -> str:
        return (
            f"<Deployment(id={self.id}, project_id={self.project_id}, "
            f"gitlab_deployment_id={self.gitlab_deployment_id}, status='{self.status}')>"
        )
