# Tasks: GitLab Metrics Dashboard

**Feature**: 001-gitlab-metrics-dashboard  
**Input**: Design documents from `/specs/001-gitlab-metrics-dashboard/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.yaml

**Tests**: Tests are included as this is a production feature requiring quality assurance per constitution requirements (80% coverage minimum).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow the web application structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create root project structure with backend/ and frontend/ directories
- [ ] T002 [P] Initialize backend Python project with pyproject.toml and requirements.txt
- [ ] T003 [P] Initialize frontend React+TypeScript project with package.json and vite.config.ts
- [ ] T004 [P] Create docker-compose.yml with PostgreSQL, Redis, backend, frontend, and worker services
- [ ] T005 [P] Create .env.example with required environment variables (DATABASE_URL, REDIS_URL, GITLAB_API_URL, SECRET_KEY)
- [ ] T006 [P] Setup backend directory structure (api/, models/, services/, tasks/, database/, config/)
- [ ] T007 [P] Setup frontend directory structure (components/, pages/, services/, types/, hooks/)
- [ ] T008 [P] Configure Black, Ruff, and mypy for backend code quality in pyproject.toml
- [ ] T009 [P] Configure ESLint, Prettier, and TypeScript for frontend in tsconfig.json and .eslintrc
- [ ] T010 [P] Create README.md with project overview and link to quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Setup PostgreSQL database schema with Alembic in backend/src/database/migrations/
- [ ] T012 [P] Create base SQLAlchemy model class in backend/src/models/__init__.py
- [ ] T013 [P] Implement database session management in backend/src/database/session.py
- [ ] T014 [P] Create FastAPI application entry point in backend/src/api/main.py
- [ ] T015 [P] Implement error handling middleware in backend/src/api/middleware/error_handler.py
- [ ] T016 [P] Implement structured logging middleware in backend/src/api/middleware/logging.py
- [ ] T017 [P] Create configuration management in backend/src/config/settings.py
- [ ] T018 [P] Implement GitLab API client wrapper in backend/src/services/gitlab_client.py
- [ ] T019 [P] Setup Celery configuration for daily batch processing in backend/src/tasks/__init__.py
- [ ] T020 [P] Create React app entry point in frontend/src/main.tsx
- [ ] T021 [P] Create main App component with routing in frontend/src/App.tsx
- [ ] T022 [P] Implement API client service (axios wrapper) in frontend/src/services/api.ts
- [ ] T023 [P] Create TypeScript types for API responses in frontend/src/types/api.ts
- [ ] T024 [P] Implement Layout component with header and sidebar in frontend/src/components/layout/Layout.tsx
- [ ] T025 [P] Create LoadingSpinner component in frontend/src/components/common/LoadingSpinner.tsx
- [ ] T026 [P] Create ErrorMessage component in frontend/src/components/common/ErrorMessage.tsx
- [ ] T027 [P] Create TimeRangeSelector component in frontend/src/components/common/TimeRangeSelector.tsx
- [ ] T028 Implement health check endpoint in backend/src/api/routes/ (required for deployment)
- [ ] T029 Add CORS configuration to FastAPI application in backend/src/api/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Four Keys Metrics (Priority: P1) 🎯 MVP

**Goal**: Enable users to view Four Keys DevOps metrics (deployment frequency, lead time, change failure rate, time to restore) for their GitLab projects

**Independent Test**: Connect to a GitLab project with deployment history, navigate to Four Keys tab, verify all four metrics display with accurate calculations over a selected time period

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T030 [P] [US1] Contract test for GET /projects/{id}/four-keys endpoint in backend/tests/contract/test_four_keys_api.py
- [ ] T031 [P] [US1] Integration test for Four Keys calculation logic in backend/tests/integration/test_four_keys_integration.py
- [ ] T032 [P] [US1] Unit test for metrics calculator service in backend/tests/unit/test_metrics_calculator.py
- [ ] T033 [P] [US1] E2E test for Four Keys tab user journey in frontend/tests/e2e/four-keys.spec.ts

### Backend Implementation for User Story 1

- [ ] T034 [P] [US1] Create Project model in backend/src/models/project.py
- [ ] T035 [P] [US1] Create FourKeysMetrics model in backend/src/models/metrics.py
- [ ] T036 [P] [US1] Create Deployment model in backend/src/models/metrics.py
- [ ] T037 [US1] Create Alembic migration for Project, FourKeysMetrics, and Deployment tables in backend/src/database/migrations/
- [ ] T038 [P] [US1] Implement metrics calculation service in backend/src/services/metrics_calculator.py
- [ ] T039 [US1] Implement data refresh orchestration in backend/src/services/data_refresh.py (depends on T038)
- [ ] T040 [P] [US1] Implement project management routes (POST, GET, DELETE) in backend/src/api/routes/projects.py
- [ ] T041 [P] [US1] Implement manual refresh route (POST /projects/{id}/refresh) in backend/src/api/routes/projects.py
- [ ] T042 [US1] Implement Four Keys metrics endpoint (GET /projects/{id}/four-keys) in backend/src/api/routes/four_keys.py
- [ ] T043 [US1] Implement daily batch refresh Celery task in backend/src/tasks/daily_refresh.py

### Frontend Implementation for User Story 1

- [ ] T044 [P] [US1] Create TypeScript interfaces for Four Keys metrics in frontend/src/types/metrics.ts
- [ ] T045 [P] [US1] Create Four Keys data fetching service in frontend/src/services/fourKeysService.ts
- [ ] T046 [P] [US1] Implement useMetrics custom hook in frontend/src/hooks/useMetrics.ts
- [ ] T047 [P] [US1] Create DeploymentFrequency chart component in frontend/src/components/four-keys/DeploymentFrequency.tsx
- [ ] T048 [P] [US1] Create LeadTimeChart component in frontend/src/components/four-keys/LeadTimeChart.tsx
- [ ] T049 [P] [US1] Create ChangeFailureRate chart component in frontend/src/components/four-keys/ChangeFailureRate.tsx
- [ ] T050 [P] [US1] Create TimeToRestore chart component in frontend/src/components/four-keys/TimeToRestore.tsx
- [ ] T051 [US1] Create FourKeysTab component integrating all charts in frontend/src/components/four-keys/FourKeysTab.tsx
- [ ] T052 [US1] Create Dashboard page with tab navigation in frontend/src/pages/Dashboard.tsx
- [ ] T053 [US1] Create ProjectSettings page for adding/managing projects in frontend/src/pages/ProjectSettings.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. This is the MVP!

---

## Phase 4: User Story 2 - View Team Member Activity and Review Load (Priority: P2)

**Goal**: Enable managers to see individual team member activity metrics and review load distribution to identify workload imbalances

**Independent Test**: Connect to a GitLab project with multiple contributors, navigate to Team Activity tab, verify commit counts, MR activity, and review load are displayed per team member

### Tests for User Story 2 ⚠️

- [ ] T054 [P] [US2] Contract test for GET /projects/{id}/team-activity endpoint in backend/tests/contract/test_team_activity_api.py
- [ ] T055 [P] [US2] Integration test for team activity analysis in backend/tests/integration/test_activity_integration.py
- [ ] T056 [P] [US2] Unit test for activity analyzer service in backend/tests/unit/test_activity_analyzer.py

### Backend Implementation for User Story 2

- [ ] T057 [P] [US2] Create TeamMember model in backend/src/models/team_member.py
- [ ] T058 [P] [US2] Create ActivityMetrics model in backend/src/models/team_member.py
- [ ] T059 [P] [US2] Create MergeRequest model in backend/src/models/team_member.py
- [ ] T060 [P] [US2] Create Review model in backend/src/models/team_member.py
- [ ] T061 [US2] Create Alembic migration for TeamMember, ActivityMetrics, MergeRequest, and Review tables in backend/src/database/migrations/
- [ ] T062 [US2] Implement activity analysis service in backend/src/services/activity_analyzer.py
- [ ] T063 [US2] Update data refresh orchestration to include team activity data in backend/src/services/data_refresh.py
- [ ] T064 [US2] Implement team activity endpoint (GET /projects/{id}/team-activity) in backend/src/api/routes/team_activity.py
- [ ] T065 [US2] Update daily batch task to include activity metrics in backend/src/tasks/daily_refresh.py

### Frontend Implementation for User Story 2

- [ ] T066 [P] [US2] Create TypeScript interfaces for team activity in frontend/src/types/team.ts
- [ ] T067 [P] [US2] Create team activity data fetching service in frontend/src/services/teamActivityService.ts
- [ ] T068 [P] [US2] Create MemberActivityTable component in frontend/src/components/team-activity/MemberActivityTable.tsx
- [ ] T069 [P] [US2] Create ReviewLoadChart component in frontend/src/components/team-activity/ReviewLoadChart.tsx
- [ ] T070 [US2] Create TeamActivityTab component integrating table and charts in frontend/src/components/team-activity/TeamActivityTab.tsx
- [ ] T071 [US2] Integrate TeamActivityTab into Dashboard page in frontend/src/pages/Dashboard.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Analyze Cycle Time (Priority: P3)

**Goal**: Enable process specialists to analyze cycle time metrics broken down by stages (coding, review, deployment) to identify bottlenecks

**Independent Test**: Connect to a GitLab project with MR history, navigate to Cycle Time Analysis tab, verify cycle time is broken down into stages with visual representations

### Tests for User Story 3 ⚠️

- [ ] T072 [P] [US3] Contract test for GET /projects/{id}/cycle-time endpoint in backend/tests/contract/test_cycle_time_api.py
- [ ] T073 [P] [US3] Integration test for cycle time analysis in backend/tests/integration/test_cycle_time_integration.py
- [ ] T074 [P] [US3] Unit test for cycle time analyzer service in backend/tests/unit/test_cycle_time_analyzer.py

### Backend Implementation for User Story 3

- [ ] T075 [US3] Implement cycle time calculation service in backend/src/services/cycle_time_analyzer.py
- [ ] T076 [US3] Update data refresh orchestration to include cycle time analysis in backend/src/services/data_refresh.py
- [ ] T077 [US3] Implement cycle time endpoint (GET /projects/{id}/cycle-time) in backend/src/api/routes/cycle_time.py
- [ ] T078 [US3] Update daily batch task to include cycle time metrics in backend/src/tasks/daily_refresh.py

### Frontend Implementation for User Story 3

- [ ] T079 [P] [US3] Create cycle time data fetching service in frontend/src/services/cycleTimeService.ts
- [ ] T080 [P] [US3] Create StageBreakdown component in frontend/src/components/cycle-time/StageBreakdown.tsx
- [ ] T081 [P] [US3] Create PercentileChart component in frontend/src/components/cycle-time/PercentileChart.tsx
- [ ] T082 [US3] Create CycleTimeTab component integrating breakdown and charts in frontend/src/components/cycle-time/CycleTimeTab.tsx
- [ ] T083 [US3] Integrate CycleTimeTab into Dashboard page in frontend/src/pages/Dashboard.tsx

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T084 [P] Add comprehensive API documentation to OpenAPI spec in backend/src/api/main.py
- [ ] T085 [P] Create user guide documentation in docs/user-guide.md
- [ ] T086 [P] Add accessibility ARIA labels to all chart components across frontend/src/components/
- [ ] T087 [P] Implement keyboard navigation for tab switching in frontend/src/pages/Dashboard.tsx
- [ ] T088 [P] Add error boundary component for graceful error handling in frontend/src/App.tsx
- [ ] T089 [P] Optimize database queries with appropriate indexes (review data-model.md for index requirements)
- [ ] T090 [P] Implement caching strategy in backend/src/services/ per research.md recommendations
- [ ] T091 [P] Add rate limiting for GitLab API calls in backend/src/services/gitlab_client.py
- [ ] T092 [P] Create Dockerfile for backend service
- [ ] T093 [P] Create Dockerfile for frontend service
- [ ] T094 [P] Add CI/CD pipeline configuration in .github/workflows/ci.yml
- [ ] T095 Validate all tests pass with 80% coverage minimum
- [ ] T096 Run quickstart.md validation to ensure setup instructions work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Reuses Project model from US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Reuses MergeRequest model from US2 but independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints/routes
- Backend endpoints before frontend services
- Frontend services before frontend components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for GET /projects/{id}/four-keys endpoint"
Task: "Integration test for Four Keys calculation logic"
Task: "Unit test for metrics calculator service"
Task: "E2E test for Four Keys tab user journey"

# Launch all models for User Story 1 together:
Task: "Create Project model in backend/src/models/project.py"
Task: "Create FourKeysMetrics model in backend/src/models/metrics.py"
Task: "Create Deployment model in backend/src/models/metrics.py"

# Launch all frontend charts for User Story 1 together:
Task: "Create DeploymentFrequency chart component"
Task: "Create LeadTimeChart component"
Task: "Create ChangeFailureRate chart component"
Task: "Create TimeToRestore chart component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 96
**Setup Tasks**: 10
**Foundational Tasks**: 19
**User Story 1 (P1) Tasks**: 24 (4 tests + 20 implementation)
**User Story 2 (P2) Tasks**: 18 (3 tests + 15 implementation)
**User Story 3 (P3) Tasks**: 12 (3 tests + 9 implementation)
**Polish Tasks**: 13

**Parallel Opportunities**: 60 tasks marked [P] can run concurrently with proper team coordination

**Independent Test Criteria**:
- US1: Four Keys metrics display with accurate calculations
- US2: Team activity metrics display per member
- US3: Cycle time breakdown with stage analysis

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 53 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach per constitution)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are absolute and follow plan.md structure
- Tests included to meet constitution requirement (80% coverage minimum)