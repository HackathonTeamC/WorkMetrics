from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseModel


class TeamMember(BaseModel):
    """Team member model to track individual contributors."""

    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    gitlab_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="team_members")
    activity_metrics: Mapped[list["ActivityMetrics"]] = relationship(
        "ActivityMetrics", back_populates="team_member", cascade="all, delete-orphan"
    )
    merge_requests: Mapped[list["MergeRequest"]] = relationship(
        "MergeRequest",
        foreign_keys="MergeRequest.author_id",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="reviewer", cascade="all, delete-orphan"
    )


class ActivityMetrics(BaseModel):
    """Activity metrics for team members over a specific time period."""

    __tablename__ = "activity_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_member_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("team_members.id", ondelete="CASCADE")
    )
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Commit activity
    commit_count: Mapped[int] = mapped_column(Integer, default=0)
    lines_added: Mapped[int] = mapped_column(Integer, default=0)
    lines_deleted: Mapped[int] = mapped_column(Integer, default=0)

    # Merge request activity
    mrs_created: Mapped[int] = mapped_column(Integer, default=0)
    mrs_merged: Mapped[int] = mapped_column(Integer, default=0)
    mrs_closed: Mapped[int] = mapped_column(Integer, default=0)

    # Review activity
    reviews_given: Mapped[int] = mapped_column(Integer, default=0)
    review_comments: Mapped[int] = mapped_column(Integer, default=0)
    avg_review_time_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    team_member: Mapped["TeamMember"] = relationship("TeamMember", back_populates="activity_metrics")


class MergeRequest(BaseModel):
    """Merge request model to track MR activity."""

    __tablename__ = "merge_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("team_members.id", ondelete="CASCADE")
    )
    gitlab_mr_id: Mapped[int] = mapped_column(Integer, nullable=False)
    gitlab_mr_iid: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)  # opened, merged, closed
    created_at_gitlab: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    merged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    target_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="merge_requests")
    author: Mapped["TeamMember"] = relationship(
        "TeamMember", foreign_keys=[author_id], back_populates="merge_requests"
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="merge_request", cascade="all, delete-orphan"
    )


class Review(BaseModel):
    """Review model to track code review activity."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merge_request_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("merge_requests.id", ondelete="CASCADE")
    )
    reviewer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("team_members.id", ondelete="CASCADE")
    )
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    approval_status: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # approved, commented, changes_requested

    # Relationships
    merge_request: Mapped["MergeRequest"] = relationship("MergeRequest", back_populates="reviews")
    reviewer: Mapped["TeamMember"] = relationship("TeamMember", back_populates="reviews")
