# WorkMetrics - GitLab Metrics Dashboard

A comprehensive metrics dashboard that integrates with GitLab to visualize development team performance indicators including Four Keys metrics, team activity, and cycle time analysis.

## 🎯 Features

### Core Metrics

- **Four Keys Metrics** (Priority: P1) 🎯 MVP
  - Deployment Frequency
  - Lead Time for Changes
  - Change Failure Rate
  - Time to Restore Service

- **Team Activity & Review Load** (Priority: P2)
  - Individual member commit counts
  - Merge request activity (created/merged)
  - Code review participation and load distribution
  - Workload balance visualization

- **Cycle Time Analysis** (Priority: P3)
  - Stage breakdown (coding, review, deployment)
  - Percentile analysis (p50, p75, p95)
  - Bottleneck identification

### Key Capabilities

- ✅ Tab-based interface for metric categories
- ✅ Time range filtering (7, 30, 90 days, custom)
- ✅ Manual data refresh + daily batch updates (2:00 AM)
- ✅ Multiple GitLab project support
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ WCAG 2.1 Level AA accessibility

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL 15 (database)
- Redis 7 (cache & task queue)
- Celery (async tasks & daily batch)
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Recharts (data visualization)
- Tailwind CSS (styling)
- Zustand (state management)
- Axios (API client)

**Infrastructure:**
- Docker & Docker Compose
- GitLab API integration

## 📋 Prerequisites

- Docker & Docker Compose
- Node.js 20+ & npm 10+ (for local frontend development)
- Python 3.11+ (for local backend development)
- GitLab account with API access token

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/HackathonTeamC/WorkMetrics.git
cd WorkMetrics
```

### 2. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```env
# Required: GitLab API Configuration
GITLAB_API_URL=https://gitlab.com/api/v4
GITLAB_ACCESS_TOKEN=your_gitlab_access_token_here

# Required: Security
SECRET_KEY=your_secret_key_here_change_in_production

# Optional: Customize other settings as needed
```

### 3. Start Services with Docker Compose

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- Celery Worker (background tasks)
- Celery Beat (scheduler)
- Frontend (port 3000)

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

### 6. Add Your First Project

1. Navigate to http://localhost:3000
2. Go to "Project Settings"
3. Click "Add Project"
4. Enter your GitLab project URL
5. Click "Refresh Data" to load initial metrics

## 🛠️ Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run development server
uvicorn src.api.main:app --reload

# Run tests
pytest

# Run linting
black .
ruff check .
mypy src/

# Create database migration
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run E2E tests
npm run test:e2e

# Run linting
npm run lint
npm run format

# Type checking
npm run typecheck

# Build for production
npm run build
```

### Run Celery Tasks Locally

```bash
# Start Celery worker
celery -A src.tasks worker --loglevel=info

# Start Celery beat (scheduler)
celery -A src.tasks beat --loglevel=info
```

## 📊 Project Structure

```
WorkMetrics/
├── backend/                 # Backend API service
│   ├── src/
│   │   ├── api/            # FastAPI routes
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   ├── tasks/          # Celery tasks
│   │   ├── database/       # DB config & migrations
│   │   └── config/         # Configuration
│   ├── tests/              # Backend tests
│   │   ├── contract/       # API contract tests
│   │   ├── integration/    # Integration tests
│   │   └── unit/           # Unit tests
│   └── pyproject.toml      # Python dependencies
├── frontend/               # Frontend React app
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API clients
│   │   ├── types/          # TypeScript types
│   │   ├── hooks/          # Custom hooks
│   │   └── utils/          # Utilities
│   ├── tests/              # Frontend tests
│   │   ├── unit/           # Unit tests
│   │   └── e2e/            # E2E tests (Playwright)
│   └── package.json        # Node dependencies
├── specs/                  # Feature specifications
│   └── 001-gitlab-metrics-dashboard/
│       ├── spec.md         # Feature spec
│       ├── plan.md         # Implementation plan
│       ├── tasks.md        # Task breakdown
│       └── ...
├── docker-compose.yml      # Docker services
├── .env.example           # Environment template
└── README.md              # This file
```

## 🧪 Testing

### Test Coverage Requirements

- **Minimum**: 80% code coverage (constitution requirement)
- **Critical paths**: 100% coverage (e.g., Four Keys calculation)

### Running All Tests

```bash
# Backend tests with coverage
cd backend
pytest --cov=src --cov-report=html

# Frontend tests with coverage
cd frontend
npm run test:coverage

# E2E tests
cd frontend
npm run test:e2e
```

## 📈 Performance Targets

- API response time: <200ms (p95)
- Initial page load: <2 seconds (3G connection)
- Tab switching: <1 second
- Support: 1000 concurrent users
- Projects: Up to 10,000 merge requests without degradation

## 🔒 Security

- All API endpoints require authentication
- GitLab access tokens stored encrypted
- HTTPS only in production
- Input validation and sanitization
- Regular dependency vulnerability scanning

## 📚 Documentation

- [Feature Specification](specs/001-gitlab-metrics-dashboard/spec.md)
- [Implementation Plan](specs/001-gitlab-metrics-dashboard/plan.md)
- [Task Breakdown](specs/001-gitlab-metrics-dashboard/tasks.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Project Constitution](.specify/memory/constitution.md)

## 🤝 Contributing

1. Review the [Project Constitution](.specify/memory/constitution.md)
2. Check [tasks.md](specs/001-gitlab-metrics-dashboard/tasks.md) for available work
3. Create a feature branch
4. Follow TDD approach (tests first!)
5. Ensure all quality gates pass
6. Submit pull request

### Quality Gates

Before merging, ensure:
- ✅ All tests pass
- ✅ Test coverage ≥ 80%
- ✅ Linting passes (Black, Ruff, ESLint)
- ✅ Type checking passes (mypy, TypeScript)
- ✅ Code review approved

## 📝 License

[Add license information]

## 🙋 Support

For issues and questions:
- GitHub Issues: [HackathonTeamC/WorkMetrics/issues](https://github.com/HackathonTeamC/WorkMetrics/issues)
- Documentation: [specs/](specs/)

---

**Current Status**: Phase 1 (Setup) Complete ✅

**Next Steps**: 
- Phase 2: Foundational infrastructure (database, API, core services)
- Phase 3: User Story 1 - Four Keys Metrics (MVP)

See [tasks.md](specs/001-gitlab-metrics-dashboard/tasks.md) for detailed implementation roadmap.