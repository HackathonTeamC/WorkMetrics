# Quickstart Guide: GitLab Metrics Dashboard

**Feature**: 001-gitlab-metrics-dashboard  
**Date**: 2025-11-21  
**Phase**: 1 - Development Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** 24.0+ and **Docker Compose** 2.20+
- **Git** 2.40+
- **Node.js** 20.x+ and **npm** 10.x+ (for local frontend development)
- **Python** 3.11+ (for local backend development)
- **GitLab Access Token** with `read_api`, `read_repository`, and `read_user` scopes

## Quick Start (Docker)

The fastest way to get the application running:

```bash
# 1. Clone the repository
git clone https://github.com/HackathonTeamC/WorkMetrics.git
cd WorkMetrics

# 2. Checkout the feature branch
git checkout 001-gitlab-metrics-dashboard

# 3. Copy environment template
cp .env.example .env

# 4. Edit .env and add your GitLab token
nano .env  # or use your preferred editor

# 5. Start all services
docker-compose up -d

# 6. Wait for services to be ready (about 30 seconds)
docker-compose logs -f backend  # Watch backend logs

# 7. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1
# API Docs: http://localhost:8000/docs
```

That's it! The application should now be running.

## Environment Configuration

Edit `.env` file with your settings:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/workmetrics

# Redis (for Celery)
REDIS_URL=redis://redis:6379/0

# GitLab Configuration
GITLAB_API_URL=https://gitlab.com/api/v4
GITLAB_DEFAULT_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx

# Application Settings
SECRET_KEY=your-secret-key-here-change-in-production
ENVIRONMENT=development
LOG_LEVEL=INFO

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Generate Secret Key

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Local Development Setup

For active development without Docker:

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements-dev.txt

# 4. Set up database
# Start PostgreSQL (using Docker)
docker run -d \
  --name workmetrics-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=workmetrics \
  -p 5432:5432 \
  postgres:15

# 5. Run database migrations
alembic upgrade head

# 6. Start Redis (for Celery)
docker run -d \
  --name workmetrics-redis \
  -p 6379:6379 \
  redis:7

# 7. Start Celery worker (in a separate terminal)
celery -A src.tasks.daily_refresh worker --loglevel=info

# 8. Start Celery beat (for scheduled tasks, in another terminal)
celery -A src.tasks.daily_refresh beat --loglevel=info

# 9. Start backend server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
# 1. Navigate to frontend directory (from repo root)
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Connecting Your First Project

1. **Get GitLab Access Token**:
   - Go to GitLab → User Settings → Access Tokens
   - Create token with scopes: `read_api`, `read_repository`, `read_user`
   - Copy the token (you won't see it again!)

2. **Add Project via UI**:
   - Open http://localhost:3000
   - Click "Add Project"
   - Enter GitLab Project ID (find it on project's main page)
   - Paste your access token
   - Click "Connect"

3. **Manual Data Refresh**:
   - Click "Refresh Data" button
   - Wait for data to load (may take 10-30 seconds for first sync)

4. **View Metrics**:
   - Navigate to "Four Keys" tab to see deployment metrics
   - Switch to "Team Activity" to see member contributions
   - Check "Cycle Time" for development process insights

## Verifying Installation

### Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-21T12:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### API Documentation

Visit `http://localhost:8000/docs` to see interactive API documentation (Swagger UI).

### Frontend Check

Visit `http://localhost:3000` - you should see the dashboard interface.

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/contract/      # Contract tests only

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run E2E tests (requires app running)
npm run test:e2e
```

## Common Issues & Solutions

### Issue: Database connection fails

**Solution**: Ensure PostgreSQL is running and connection string is correct:
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Test connection
psql postgresql://postgres:postgres@localhost:5432/workmetrics -c "SELECT 1;"
```

### Issue: GitLab API rate limit errors

**Solution**: Rate limits are 300 req/min for authenticated users. Wait 1 minute or:
- Use a higher-tier GitLab account
- Enable caching in `.env`: `CACHE_TTL=3600`

### Issue: Frontend can't connect to backend

**Solution**: Check CORS settings and API URL:
```bash
# Verify backend is accessible
curl http://localhost:8000/health

# Check frontend API URL in .env
cat frontend/.env | grep VITE_API_BASE_URL
```

### Issue: Celery tasks not running

**Solution**: Ensure Redis is running and Celery worker is started:
```bash
# Check Redis
redis-cli ping  # Should return "PONG"

# Check Celery worker logs
celery -A src.tasks.daily_refresh inspect active
```

## Development Workflow

### Making Changes

1. **Backend changes**:
   - Edit files in `backend/src/`
   - Backend auto-reloads with `--reload` flag
   - Write tests in `backend/tests/`

2. **Frontend changes**:
   - Edit files in `frontend/src/`
   - Vite provides hot module replacement (HMR)
   - Write tests alongside components

3. **Database schema changes**:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of change"
   alembic upgrade head
   ```

### Code Quality Checks

```bash
# Backend
cd backend
black src tests         # Format code
ruff check src tests    # Lint code
mypy src               # Type check

# Frontend
cd frontend
npm run lint           # ESLint
npm run format         # Prettier
npm run typecheck      # TypeScript check
```

## Daily Batch Processing

The system automatically refreshes data daily at 2:00 AM (configurable).

### Manual Trigger for Testing

```bash
# Trigger batch refresh for a specific project
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/refresh
```

### Monitor Batch Jobs

```bash
# View Celery task queue
celery -A src.tasks.daily_refresh inspect active

# View scheduled tasks
celery -A src.tasks.daily_refresh inspect scheduled
```

## Stopping the Application

### Docker

```bash
docker-compose down

# Remove volumes (database data)
docker-compose down -v
```

### Local Development

```bash
# Stop each service with Ctrl+C
# Backend: Ctrl+C in uvicorn terminal
# Frontend: Ctrl+C in npm terminal
# Celery worker: Ctrl+C in celery terminal
# Celery beat: Ctrl+C in celery beat terminal

# Stop Docker services
docker stop workmetrics-db workmetrics-redis
```

## Next Steps

- **Implement Features**: See [tasks.md](./tasks.md) for implementation tasks (created by `/speckit.tasks`)
- **Review Architecture**: See [data-model.md](./data-model.md) for data model details
- **API Reference**: See [contracts/api.yaml](./contracts/api.yaml) for complete API spec
- **Learn More**: See [research.md](./research.md) for technology decisions and best practices

## Getting Help

- **Issues**: Check the GitHub Issues page
- **Documentation**: Review [spec.md](./spec.md) for feature requirements
- **API Docs**: Visit http://localhost:8000/docs when backend is running
- **Logs**: Use `docker-compose logs -f [service]` to view logs

## Useful Commands Cheat Sheet

```bash
# Docker
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose logs -f backend    # View backend logs
docker-compose restart backend    # Restart backend service

# Database
docker exec -it workmetrics-db psql -U postgres -d workmetrics
alembic upgrade head              # Run migrations
alembic downgrade -1              # Rollback one migration

# Backend
uvicorn src.api.main:app --reload  # Start with auto-reload
pytest                             # Run tests
black .                            # Format code

# Frontend
npm run dev                        # Start dev server
npm run build                      # Production build
npm run test                       # Run tests

# Celery
celery -A src.tasks.daily_refresh worker --loglevel=info
celery -A src.tasks.daily_refresh beat --loglevel=info
celery -A src.tasks.daily_refresh inspect active
```