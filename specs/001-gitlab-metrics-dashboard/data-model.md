# Data Model: GitLab Metrics Dashboard

**Feature**: 001-gitlab-metrics-dashboard  
**Date**: 2025-11-21  
**Phase**: 1 - Data Model Design

## Overview

This document defines the data entities, relationships, and validation rules for the GitLab Metrics Dashboard application. All models support the requirements defined in [spec.md](./spec.md).

## Core Entities

### Project

Represents a connected GitLab project being monitored.

**Attributes**:
- `id` (UUID, Primary Key): Internal unique identifier
- `gitlab_project_id` (Integer, Unique, Not Null): GitLab project ID
- `name` (String, Not Null): Project name from GitLab
- `url` (String, Not Null): GitLab project URL
- `gitlab_token` (String, Encrypted, Not Null): GitLab access token for this project
- `last_sync_at` (Timestamp, Nullable): Last successful data synchronization timestamp
- `created_at` (Timestamp, Not Null): Record creation timestamp
- `updated_at` (Timestamp, Not Null): Record last update timestamp

**Validation Rules**:
- `gitlab_project_id` must be positive integer
- `url` must be valid URL format
- `gitlab_token` must be encrypted at rest
- `name` max length 255 characters

**Relationships**:
- One-to-Many with `FourKeysMetrics`
- One-to-Many with `TeamMember`
- One-to-Many with `MergeRequest`
- One-to-Many with `Deployment`

**Indexes**:
- Primary key on `id`
- Unique index on `gitlab_project_id`

---

### FourKeysMetrics

Aggregated Four Keys metrics for a project and time period.

**Attributes**:
- `id` (UUID, Primary Key): Internal unique identifier
- `project_id` (UUID, Foreign Key → Project, Not Null): Associated project
- `time_period_start` (Date, Not Null): Start date of measurement period
- `time_period_end` (Date, Not Null): End date of measurement period
- `deployment_frequency` (Decimal, Not Null): Deployments per day
- `lead_time_hours` (Decimal, Not Null): Average lead time in hours
- `change_failure_rate` (Decimal, Not Null): Percentage (0-100)
- `mean_time_to_restore_hours` (Decimal, Not Null): Average MTTR in hours
- `total_deployments` (Integer, Not Null): Total deployment count in period
- `successful_deployments` (Integer, Not Null): Successful deployment count
- `failed_deployments` (Integer, Not Null): Failed deployment count
- `calculated_at` (Timestamp, Not Null): When metrics were calculated
- `created_at` (Timestamp, Not Null): Record creation timestamp

**Validation Rules**:
- `time_period_end` must be after `time_period_start`
- `deployment_frequency` >= 0
- `lead_time_hours` >= 0
- `change_failure_rate` between 0 and 100
- `mean_time_to_restore_hours` >= 0
- `total_deployments` = `successful_deployments` + `failed_deployments`
- `successful_deployments` >= 0
- `failed_deployments` >= 0

**Relationships**:
- Many-to-One with `Project`

**Indexes**:
- Primary key on `id`
- Composite index on `(project_id, time_period_start, time_period_end)`
- Index on `calculated_at` for cache expiration queries

---

### TeamMember

Represents an individual contributor to a project.

**Attributes**:
- `id` (UUID, Primary Key): Internal unique identifier
- `project_id` (UUID, Foreign Key → Project, Not Null): Associated project
- `gitlab_user_id` (Integer, Not Null): GitLab user ID
- `username` (String, Not Null): GitLab username
- `name` (String, Not Null): Full name from GitLab
- `email` (String, Nullable): Email address
- `avatar_url` (String, Nullable): Profile picture URL
- `is_active` (Boolean, Not Null, Default: True): Whether user is currently active
- `created_at` (Timestamp, Not Null): Record creation timestamp
- `updated_at` (Timestamp, Not Null): Record last update timestamp

**Validation Rules**:
- `gitlab_user_id` must be positive integer
- `username` max length 255 characters
- `name` max length 255 characters
- `email` must be valid email format if provided
- Composite unique constraint on `(project_id, gitlab_user_id)`

**Relationships**:
- Many-to-One with `Project`
- One-to-Many with `ActivityMetrics`
- One-to-Many with `MergeRequest` (as author)
- One-to-Many with `Review` (as reviewer)

**Indexes**:
- Primary key on `id`
- Composite unique index on `(project_id, gitlab_user_id)`
- Index on `username` for search queries

---

### ActivityMetrics

Time-bound activity data for a team member.

**Attributes**:
- `id` (UUID, Primary Key): Internal unique identifier
- `team_member_id` (UUID, Foreign Key → TeamMember, Not Null): Associated team member
- `time_period_start` (Date, Not Null): Start date of measurement period
- `time_period_end` (Date, Not Null): End date of measurement period
- `commit_count` (Integer, Not Null): Number of commits
- `merge_requests_created` (Integer, Not Null): MRs created count
- `merge_requests_merged` (Integer, Not Null): MRs merged count
- `reviews_completed` (Integer, Not Null): Code reviews completed
- `comments_written` (Integer, Not Null): Review comments written
- `lines_added` (Integer, Not Null): Lines of code added
- `lines_removed` (Integer, Not Null): Lines of code removed
- `calculated_at` (Timestamp, Not Null): When metrics were calculated
- `created_at` (Timestamp, Not Null): Record creation timestamp

**Validation Rules**:
- `time_period_end` must be after `time_period_start`
- All count fields >= 0
- `merge_requests_merged` <= `merge_requests_created`

**Relationships**:
- Many-to-One with `TeamMember`

**Indexes**:
- Primary key on `id`
- Composite index on `(team_member_id, time_period_start, time_period_end)`
- Index on `calculated_at` for cache expiration queries

---

### MergeRequest

Represents a GitLab merge request.

**Attributes**:
- `id` (UUID, Primary Key): Internal unique identifier
- `project_id` (UUID, Foreign Key → Project, Not Null): Associated project
- `gitlab_mr_id` (Integer, Not Null): GitLab merge request IID
- `author_id` (UUID, Foreign Key → TeamMember, Not Null): MR author
- `title` (String, Not Null): MR title
- `state` (Enum: opened, merged, closed, Not Null): Current state
- `created_at_gitlab` (Timestamp, Not Null): When MR was created in GitLab
- `merged_at` (Timestamp, Nullable): When MR was merged
- `closed_at` (Timestamp, Nullable): When MR was closed
- `first_commit_at` (Timestamp, Not Null): Timestamp of first commit
- `first_review_at` (Timestamp, Nullable): Timestamp of first review comment
- `approved_at` (Timestamp, Nullable): When MR was approved
- `deployment_at` (Timestamp, Nullable): When changes were deployed
- `target_branch` (String, Not Null): Target branch name
- `source_branch` (String, Not Null): Source branch name
- `created_at` (Timestamp, Not Null): Record creation timestamp
- `updated_at` (Timestamp, Not Null): Record last update timestamp

**Validation Rules**:
- `gitlab_mr_id` must be positive integer
- Composite unique constraint on `(project_id, gitlab_mr_id)`
- `title` max length 512 characters
- `merged_at` must be after `created_at_gitlab` if set
- `approved_at` must be after `created_at_gitlab` if set
- `deployment_at` must be after `merged_at` if set

**Relationships**:
- Many-to-One with `Project`
- Many-to-One with `TeamMember` (author)
- One-to-Many with `Review`

**Indexes**:
- Primary key on `id`
- Composite unique index on `(project_id, gitlab_mr_id)`
- Index on `created_at_gitlab` for time range queries
- Index on `merged_at` for Four Keys calculations
- Index on `state` for filtering

**Derived Metrics** (calculated, not stored):
- `coding_time`: `created_at_gitlab - first_commit_at`
- `review_time`: `approved_at - first_review_at` (or `merged_at - first_review_at` if no approval)
- `deployment_time`: `deployment_at - merged_at`
- `total_cycle_time`: `deployment_at - first_commit_at`
- `lead_time`: `deployment_at - first_commit_at`

---

### Review

Represents a code review on a merge request.

**Attributes**:
- `id` (UUID, Primary Key): Internal unique identifier
- `merge_request_id` (UUID, Foreign Key → MergeRequest, Not Null): Associated MR
- `reviewer_id` (UUID, Foreign Key → TeamMember, Not Null): Reviewer
- `reviewed_at` (Timestamp, Not Null): When review was submitted
- `state` (Enum: commented, approved, requested_changes, Not Null): Review state
- `comment_count` (Integer, Not Null): Number of comments in review
- `created_at` (Timestamp, Not Null): Record creation timestamp

**Validation Rules**:
- `comment_count` >= 0
- `reviewed_at` must be after MR `created_at_gitlab`

**Relationships**:
- Many-to-One with `MergeRequest`
- Many-to-One with `TeamMember` (reviewer)

**Indexes**:
- Primary key on `id`
- Composite index on `(merge_request_id, reviewer_id)`
- Index on `reviewed_at` for activity metrics

---

### Deployment

Represents a deployment event.

**Attributes**:
- `id` (UUID, Primary Key): Internal unique identifier
- `project_id` (UUID, Foreign Key → Project, Not Null): Associated project
- `gitlab_deployment_id` (Integer, Nullable): GitLab deployment ID (if available)
- `gitlab_pipeline_id` (Integer, Not Null): Associated pipeline ID
- `environment` (String, Not Null): Deployment environment (production, staging, etc.)
- `status` (Enum: success, failed, canceled, Not Null): Deployment status
- `deployed_at` (Timestamp, Not Null): Deployment timestamp
- `commit_sha` (String, Not Null): Git commit SHA
- `merge_request_ids` (JSON, Nullable): Array of MR IIDs included in deployment
- `created_at` (Timestamp, Not Null): Record creation timestamp

**Validation Rules**:
- `gitlab_pipeline_id` must be positive integer
- Composite unique constraint on `(project_id, gitlab_pipeline_id)`
- `environment` max length 100 characters
- `commit_sha` must be valid git SHA format (40 hex characters)

**Relationships**:
- Many-to-One with `Project`
- Logical relationship with `MergeRequest` via `merge_request_ids`

**Indexes**:
- Primary key on `id`
- Composite unique index on `(project_id, gitlab_pipeline_id)`
- Index on `deployed_at` for time range queries
- Index on `environment` for filtering production deployments
- Index on `status` for Four Keys calculations

---

### TimeRange

User preference for time range filtering (session/local storage, not persisted).

**Attributes**:
- `start_date` (Date, Not Null): Start of time range
- `end_date` (Date, Not Null): End of time range
- `preset` (Enum: last_7_days, last_30_days, last_90_days, custom, Nullable): Preset option

**Validation Rules**:
- `end_date` must be after or equal to `start_date`
- `end_date` cannot be in the future
- If `preset` is not 'custom', dates must match preset calculation

**Note**: This entity is not stored in the database; it's a frontend state object.

---

## Entity Relationships Diagram

```
Project (1) ──< (N) FourKeysMetrics
   │
   ├──< (N) TeamMember (1) ──< (N) ActivityMetrics
   │                     │
   │                     └──< (N) Review
   │
   ├──< (N) MergeRequest (1) ──< (N) Review
   │                     │
   │                     └──> (1) TeamMember (author)
   │
   └──< (N) Deployment
```

## Data Lifecycle

### Data Ingestion Flow

1. **Manual Refresh** (User-initiated):
   - User clicks refresh button
   - Backend fetches data from GitLab API
   - Data stored/updated in database
   - Metrics calculated and cached

2. **Daily Batch** (Automated):
   - Celery task runs at configured time (e.g., 2 AM)
   - For each active project:
     - Fetch incremental data from GitLab (since last sync)
     - Update/insert new records
     - Recalculate metrics for affected time periods
     - Update `last_sync_at` timestamp

### Cache Invalidation

- **Historical Data** (>30 days old): 24-hour cache TTL
- **Recent Data** (<30 days old): 1-hour cache TTL
- **Real-time Data** (today): No cache, always calculate
- **Manual Refresh**: Clears all cache for project

### Data Retention

- **Raw Data** (MRs, Reviews, Deployments): 90 days
- **Aggregated Metrics**: 1 year
- **Audit Logs**: 180 days

Automated cleanup job runs weekly to remove old records.

## State Transitions

### MergeRequest State Machine

```
opened → merged (success path)
opened → closed (abandoned)
closed → opened (reopened)
merged → (terminal state)
```

### Deployment Status

```
pending → running → success (success path)
pending → running → failed (failure path)
pending → canceled (canceled before running)
```

## Data Validation Layer

### API Level (FastAPI Pydantic Models)

- Type validation
- Required field enforcement
- Range validation (e.g., percentages 0-100)
- Format validation (e.g., email, URL)

### Database Level (SQLAlchemy Constraints)

- Foreign key constraints
- Unique constraints
- Not null constraints
- Check constraints (e.g., `end_date > start_date`)

### Business Logic Level (Service Layer)

- Cross-entity validation
- State transition validation
- Business rule enforcement

## Performance Considerations

### Query Optimization

1. **Time Range Queries**: Always include date range in WHERE clause
2. **Aggregations**: Pre-calculate and cache when possible
3. **Join Optimization**: Use appropriate indexes on foreign keys
4. **Pagination**: Implement cursor-based pagination for large result sets

### Denormalization Decisions

- **ActivityMetrics**: Pre-aggregated to avoid expensive JOIN queries
- **FourKeysMetrics**: Pre-calculated to meet <200ms response time requirement
- Trade-off: Storage space for query performance

## Migration Strategy

### Initial Schema

1. Create all tables with constraints
2. Create indexes
3. Seed configuration data

### Future Migrations

- Use Alembic for schema versioning
- Always provide rollback migrations
- Test migrations on copy of production data

## Next Steps

- **Phase 1**: Define API contracts (contracts/api.yaml)
- **Phase 1**: Write quickstart guide (quickstart.md)
- **Phase 2**: Break down into implementation tasks (tasks.md)