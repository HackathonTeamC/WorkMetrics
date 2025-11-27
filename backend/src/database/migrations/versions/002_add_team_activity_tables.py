"""add team activity tables

Revision ID: 002_add_team_activity
Revises: 001_create_initial_tables
Create Date: 2024-11-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_team_activity'
down_revision = '001_create_initial_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create team_members table
    op.create_table(
        'team_members',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('gitlab_user_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_team_members_project_id', 'team_members', ['project_id'])
    op.create_index('ix_team_members_gitlab_user_id', 'team_members', ['gitlab_user_id'])

    # Create activity_metrics table
    op.create_table(
        'activity_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('team_member_id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('commit_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('lines_added', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('lines_deleted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mrs_created', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mrs_merged', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mrs_closed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reviews_given', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('review_comments', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_review_time_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['team_member_id'], ['team_members.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_activity_metrics_team_member_id', 'activity_metrics', ['team_member_id'])
    op.create_index('ix_activity_metrics_period', 'activity_metrics', ['period_start', 'period_end'])

    # Create merge_requests table
    op.create_table(
        'merge_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('gitlab_mr_id', sa.Integer(), nullable=False),
        sa.Column('gitlab_mr_iid', sa.Integer(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('created_at_gitlab', sa.DateTime(timezone=True), nullable=False),
        sa.Column('merged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_branch', sa.String(length=255), nullable=False),
        sa.Column('target_branch', sa.String(length=255), nullable=False),
        sa.Column('additions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('deletions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['team_members.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'gitlab_mr_id', name='uq_merge_requests_project_gitlab_mr')
    )
    op.create_index('ix_merge_requests_project_id', 'merge_requests', ['project_id'])
    op.create_index('ix_merge_requests_author_id', 'merge_requests', ['author_id'])
    op.create_index('ix_merge_requests_state', 'merge_requests', ['state'])

    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('merge_request_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('comment_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('approval_status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['merge_request_id'], ['merge_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['team_members.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reviews_merge_request_id', 'reviews', ['merge_request_id'])
    op.create_index('ix_reviews_reviewer_id', 'reviews', ['reviewer_id'])


def downgrade() -> None:
    op.drop_table('reviews')
    op.drop_table('merge_requests')
    op.drop_table('activity_metrics')
    op.drop_table('team_members')
