# Research: GitLab Metrics Dashboard

**Feature**: 001-gitlab-metrics-dashboard  
**Date**: 2025-11-21  
**Phase**: 0 - Technology Research & Decision Making

## Overview

This document consolidates research findings for technology choices, best practices, and architectural decisions for the GitLab Metrics Dashboard application.

## Technology Stack Decisions

### Backend Framework: FastAPI

**Decision**: Use FastAPI 0.104+ for the backend REST API

**Rationale**:
- **Async Support**: Native async/await for efficient I/O operations (GitLab API calls)
- **Performance**: One of the fastest Python frameworks, meets <200ms p95 requirement
- **Type Safety**: Automatic validation using Pydantic models aligns with constitution
- **OpenAPI**: Auto-generated API documentation satisfies documentation requirements
- **Developer Experience**: Fast development with automatic request validation and serialization

**Alternatives Considered**:
- **Django REST Framework**: More batteries-included but slower and synchronous by default
- **Flask**: Simpler but requires more manual setup for async and validation
- **Rejected because**: FastAPI provides better performance and built-in features for our needs

### Frontend Framework: React + TypeScript

**Decision**: Use React 18.x with TypeScript 5.x

**Rationale**:
- **Type Safety**: TypeScript enforces type checking, meets constitution code quality requirements
- **Component Reusability**: React's component model enables consistent UI patterns
- **Ecosystem**: Rich ecosystem for data visualization (Recharts) and UI components
- **Performance**: Virtual DOM and React 18 concurrent features support responsive UI
- **Testing**: Excellent testing tools (Vitest, React Testing Library, Playwright)

**Alternatives Considered**:
- **Vue.js**: Good but smaller ecosystem for enterprise dashboards
- **Angular**: More opinionated and heavier for this use case
- **Svelte**: Smaller bundle but less mature ecosystem for data visualization
- **Rejected because**: React offers best balance of performance, type safety, and tooling

### Database: PostgreSQL 15+

**Decision**: Use PostgreSQL for metrics data storage

**Rationale**:
- **Relational Model**: Metrics have clear relationships (projects → members → activities)
- **JSON Support**: Flexible storage for GitLab API responses
- **Performance**: Excellent query optimization with indexes
- **Aggregation**: Strong support for time-series aggregations needed for metrics
- **Reliability**: ACID compliance ensures data consistency

**Alternatives Considered**:
- **SQLite**: Simple but limited concurrency for 1000 users target
- **MongoDB**: NoSQL flexibility not needed, harder to enforce data integrity
- **TimescaleDB**: Specialized time-series but adds complexity for standard queries
- **Rejected because**: PostgreSQL provides best balance of features and simplicity

### Data Visualization: Recharts

**Decision**: Use Recharts for chart rendering

**Rationale**:
- **React Integration**: Built specifically for React, composable chart components
- **Responsive**: Built-in responsive behavior for mobile/tablet/desktop
- **Customizable**: Easy to style with Tailwind CSS
- **Accessibility**: Better accessibility support than alternatives
- **Performance**: Efficient SVG rendering for our data volumes

**Alternatives Considered**:
- **Chart.js**: Canvas-based, less React-friendly
- **D3.js**: More powerful but steeper learning curve and more code
- **Victory**: Similar to Recharts but less actively maintained
- **Rejected because**: Recharts offers best React integration and accessibility

### Task Queue: Celery

**Decision**: Use Celery with Redis for daily batch processing

**Rationale**:
- **Scheduling**: Built-in support for periodic tasks (daily refresh)
- **Reliability**: Mature, battle-tested for background jobs
- **Monitoring**: Flower provides task monitoring dashboard
- **Scalability**: Can scale workers independently

**Alternatives Considered**:
- **APScheduler**: Simpler but less robust for distributed systems
- **Dramatiq**: Modern but smaller community
- **Rejected because**: Celery is industry standard for Python background tasks

## GitLab API Integration Best Practices

### Research: GitLab API Patterns

**Key Findings**:
1. **Rate Limiting**: 300 requests/minute for authenticated users
2. **Pagination**: Uses keyset pagination for large result sets
3. **Authentication**: Personal access tokens or OAuth2
4. **Webhooks**: Available for real-time updates (future enhancement)

**Implementation Strategy**:
- Use `python-gitlab` library for API abstraction
- Implement exponential backoff for rate limit handling
- Cache API responses in PostgreSQL to minimize calls
- Batch requests where possible (e.g., fetch all MRs in one call)

### Four Keys Metrics Calculation

**Research Findings**:

1. **Deployment Frequency**:
   - Source: GitLab deployments API or pipeline completions
   - Calculation: Count deployments per time period (day/week/month)
   - Challenge: Identifying "production" deployments vs staging

2. **Lead Time for Changes**:
   - Source: Commit timestamp to deployment timestamp
   - Calculation: Average time from first commit in MR to deployment
   - Challenge: Linking commits to deployments

3. **Change Failure Rate**:
   - Source: Failed vs successful deployments
   - Calculation: (Failed deployments / Total deployments) × 100
   - Challenge: Defining "failure" (rollback, hotfix, incident)

4. **Time to Restore Service**:
   - Source: Incident timestamps to resolution timestamps
   - Calculation: Average time from incident detection to resolution
   - Challenge: Incident data might be in external systems (PagerDuty, Jira)

**Best Practices**:
- Use deployment tags/labels to identify production deployments
- Link commits to deployments via pipeline data
- Configure failure detection criteria (failed pipelines, rollbacks)
- Provide manual incident input if external systems not integrated

### Cycle Time Analysis

**Research Findings**:

**Stages**:
1. **Coding Time**: MR created timestamp - first commit timestamp
2. **Review Time**: First review comment - MR created timestamp
3. **Deployment Time**: Merged timestamp - approved timestamp

**Best Practices**:
- Use MR events API for accurate timestamps
- Handle edge cases (MRs without reviews, immediate merges)
- Provide percentile views (p50, p75, p95) to identify outliers

## Performance Optimization Strategies

### Caching Strategy

**Decision**: Multi-layer caching approach

1. **Database Cache**: Store fetched GitLab data with timestamps
2. **Query Cache**: Cache aggregated metrics calculations
3. **TTL Strategy**: 24-hour cache for historical data, 1-hour for recent data

**Rationale**: Reduces GitLab API calls, improves response time

### Database Indexing

**Required Indexes**:
- `projects(gitlab_project_id)`
- `metrics(project_id, timestamp)`
- `team_members(project_id, user_id)`
- `merge_requests(project_id, created_at, merged_at)`

**Rationale**: Optimize common queries for time-range filtering

### Async Processing

**Decision**: Use FastAPI async endpoints with asyncio

**Pattern**:
```python
async def get_four_keys(project_id: int, time_range: TimeRange):
    # Fetch from cache or database
    cached = await cache.get(project_id, time_range)
    if cached:
        return cached
    
    # Calculate and cache
    metrics = await calculate_metrics(project_id, time_range)
    await cache.set(project_id, time_range, metrics)
    return metrics
```

## Security Considerations

### Token Storage

**Decision**: Environment variables for GitLab tokens, per-user encryption for stored tokens

**Best Practices**:
- Never log tokens
- Use short-lived tokens where possible
- Implement token rotation mechanism
- Store encrypted tokens in database with user-specific encryption keys

### API Security

**Decision**: Implement API authentication for frontend-backend communication

**Pattern**:
- JWT tokens for session management
- CORS configuration for frontend domain
- Rate limiting on API endpoints

## Testing Strategy

### Unit Testing

**Scope**: Individual functions and classes
**Tools**: pytest, pytest-asyncio
**Coverage Target**: 80% minimum, 100% for calculation logic

**Key Areas**:
- Metrics calculation functions
- Data transformation logic
- API response parsing

### Integration Testing

**Scope**: Component interactions
**Tools**: pytest with test database, httpx for API testing

**Key Areas**:
- GitLab API client with mock server
- Database operations
- API endpoint flows

### Contract Testing

**Scope**: API contract validation
**Tools**: pytest with OpenAPI schema validation

**Key Areas**:
- Verify API responses match OpenAPI spec
- Ensure backward compatibility

### E2E Testing

**Scope**: Complete user workflows
**Tools**: Playwright

**Key Areas**:
- Four Keys tab displays correctly
- Time range filtering works
- Tab switching is responsive

## Accessibility Implementation

### WCAG 2.1 Level AA Compliance

**Required Features**:
1. **Keyboard Navigation**: All interactive elements accessible via Tab/Arrow keys
2. **Screen Reader Support**: ARIA labels for charts and metrics
3. **Color Contrast**: Minimum 4.5:1 ratio for text
4. **Focus Indicators**: Visible focus states for all interactive elements

**Implementation**:
- Use semantic HTML elements
- Add ARIA labels to Recharts components
- Test with screen readers (NVDA, VoiceOver)
- Provide text alternatives for visual data

## Deployment Architecture

### Docker Containers

**Services**:
1. **Backend**: FastAPI application
2. **Frontend**: Nginx serving React build
3. **Database**: PostgreSQL
4. **Cache/Queue**: Redis (for Celery)
5. **Worker**: Celery worker for batch processing

**Orchestration**: Docker Compose for development, Kubernetes for production

### Environment Configuration

**Required Environment Variables**:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `GITLAB_API_URL`: GitLab instance URL
- `GITLAB_TOKEN`: Default GitLab access token (optional)
- `SECRET_KEY`: JWT signing key

## Open Questions Resolved

All technical clarifications have been addressed through research:

1. ✅ **Data Refresh Strategy**: Manual initial + daily batch (specified in spec)
2. ✅ **Technology Stack**: FastAPI + React + PostgreSQL (researched and decided)
3. ✅ **Four Keys Calculation**: Based on GitLab deployments and pipeline data
4. ✅ **Rate Limit Handling**: Exponential backoff + caching strategy
5. ✅ **Scalability**: Async processing + database optimization + caching

## Next Steps

- **Phase 1**: Create detailed data models (data-model.md)
- **Phase 1**: Define API contracts (contracts/api.yaml)
- **Phase 1**: Write quickstart guide (quickstart.md)
- **Phase 2**: Break down into implementation tasks (tasks.md)