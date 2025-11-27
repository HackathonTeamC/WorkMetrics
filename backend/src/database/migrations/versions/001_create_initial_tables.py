"""create initial tables

Revision ID: 001
Revises: 
Create Date: 2024-11-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('gitlab_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=512), nullable=False),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('gitlab_id')
    )
    op.create_index(op.f('ix_projects_gitlab_id'), 'projects', ['gitlab_id'], unique=True)

    # Create four_keys_metrics table
    op.create_table(
        'four_keys_metrics',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.BigInteger(), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deployment_frequency', sa.Float(), nullable=False),
        sa.Column('deployment_count', sa.BigInteger(), nullable=False),
        sa.Column('lead_time_hours', sa.Float(), nullable=True),
        sa.Column('lead_time_median_hours', sa.Float(), nullable=True),
        sa.Column('change_failure_rate', sa.Float(), nullable=True),
        sa.Column('failed_deployment_count', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('time_to_restore_hours', sa.Float(), nullable=True),
        sa.Column('time_to_restore_median_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_four_keys_metrics_project_id'), 'four_keys_metrics', ['project_id'], unique=False)

    # Create deployments table
    op.create_table(
        'deployments',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.BigInteger(), nullable=False),
        sa.Column('gitlab_deployment_id', sa.BigInteger(), nullable=False),
        sa.Column('environment', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('commit_sha', sa.String(length=40), nullable=False),
        sa.Column('merge_request_iid', sa.BigInteger(), nullable=True),
        sa.Column('is_failure', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('lead_time_hours', sa.Float(), nullable=True),
        sa.Column('time_to_restore_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deployments_project_id'), 'deployments', ['project_id'], unique=False)
    op.create_index(op.f('ix_deployments_gitlab_deployment_id'), 'deployments', ['gitlab_deployment_id'], unique=False)
    op.create_index(op.f('ix_deployments_deployed_at'), 'deployments', ['deployed_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_deployments_deployed_at'), table_name='deployments')
    op.drop_index(op.f('ix_deployments_gitlab_deployment_id'), table_name='deployments')
    op.drop_index(op.f('ix_deployments_project_id'), table_name='deployments')
    op.drop_table('deployments')
    
    op.drop_index(op.f('ix_four_keys_metrics_project_id'), table_name='four_keys_metrics')
    op.drop_table('four_keys_metrics')
    
    op.drop_index(op.f('ix_projects_gitlab_id'), table_name='projects')
    op.drop_table('projects')
