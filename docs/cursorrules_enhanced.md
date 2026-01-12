# Project: Crawler Management Platform (FastAPI + React + TypeScript)
# Goal: Build a production-grade, asynchronous crawler system with real-time Web UI.
# Duration: 2 months | Current Phase: 1 (FastAPI + Async Basics)

# =============================================================================
# 1. TECHNOLOGY STACK & CONSTRAINTS
# =============================================================================

## Backend Stack:
# - Framework: FastAPI (ASYNC is MANDATORY - no sync routes)
# - Validation: Pydantic v2 (strict mode)
# - Database: SQLAlchemy with AsyncSession (SQLite for Phase 1, Postgres for Phase 2)
# - Task Queue: BackgroundTasks (Phase 1) → Celery + Redis (Phase 2)
# - HTTP Client: httpx (ASYNC only, never requests library)
# - Authentication: JWT tokens with python-jose
# - Logging: Python logging module (structured JSON logs recommended)

## Frontend Stack:
# - Framework: React 18+ (Latest)
# - Language: TypeScript (strict: true in tsconfig.json)
# - State Management: React Context API or Zustand (NO Redux in Phase 1)
# - Styling: Tailwind CSS or CSS Modules (consistent throughout)
# - Communication: fetch API + WebSocket (reconnect on disconnect)
# - Build: Vite or Create React App (Vite preferred for speed)

## Deployment Stack (Phase 2):
# - Containerization: Docker + Docker Compose
# - ASGI Server: Uvicorn + Gunicorn (4 workers recommended)
# - Cloud: Render, Railway, or AWS (auto-deployment from GitHub)

# =============================================================================
# 2. CODING STANDARDS & BEST PRACTICES
# =============================================================================

## General Rules (Python & TypeScript):
# ✅ DO: Type hints MANDATORY for all functions (args, return types)
# ✅ DO: Google-style docstrings for complex logic (3+ lines)
# ✅ DO: Specific exception handling (ValueError, HTTPException, ConnectionError)
# ✅ DO: Environment variables for all secrets (os.getenv, .env file)
# ❌ DON'T: Bare 'except:' or generic Exception catching
# ❌ DON'T: Hardcode API keys, passwords, database URLs
# ❌ DON'T: Print statements in backend (use logging)
# ❌ DON'T: Synchronous operations in async context

## Python / FastAPI Specific:
# ✅ DO: Use 'async def' for all route handlers
# ✅ DO: Use 'await' for I/O (database, HTTP, file operations)
# ✅ DO: Define Pydantic models for request/response bodies
# ✅ DO: Implement proper error responses (HTTPException with status codes)
# ✅ DO: Use Dependency Injection (Depends) for cross-cutting concerns
# ✅ DO: Separate concerns: Routes → Services → CRUD → Models
# ✅ DO: Add __all__ to modules for explicit exports
# ❌ DON'T: Use requests library (sync) - use httpx (async)
# ❌ DON'T: Return raw SQLAlchemy models in API responses
# ❌ DON'T: Use sleep in routes (use BackgroundTasks instead)
# ❌ DON'T: Make external HTTP calls in sync functions

## TypeScript / React Specific:
# ✅ DO: Functional components with Hooks (no class components)
# ✅ DO: Define interfaces for all props, state, and API responses
# ✅ DO: Extract hooks into separate files (useWebSocket, useCrawler, etc.)
# ✅ DO: Implement proper error boundaries for React components
# ✅ DO: Add loading and error states to all async operations
# ✅ DO: Memoize expensive computations (useMemo, useCallback)
# ❌ DON'T: Use 'any' type (use 'unknown' if necessary)
# ❌ DON'T: Direct DOM manipulation (use React refs)
# ❌ DON'T: Create infinite useEffect loops (check dependencies)
# ❌ DON'T: Make HTTP calls in render (use useEffect)

## Database Best Practices:
# ✅ DO: Use AsyncSession for all database operations
# ✅ DO: Use context managers: 'async with get_db() as session:'
# ✅ DO: Define separate Pydantic schemas for API (not SQLAlchemy models)
# ✅ DO: Implement proper database indexes on frequently queried fields
# ✅ DO: Use migrations (Alembic) for schema changes
# ❌ DON'T: Expose SQLAlchemy models directly in API responses
# ❌ DON'T: Use synchronous session in async context

## Error Handling & Logging:
# ✅ DO: Log all errors with context (logger.error(..., exc_info=True))
# ✅ DO: Return appropriate HTTP status codes (400, 401, 403, 404, 500)
# ✅ DO: Validate input on both client (React) and server (Pydantic)
# ✅ DO: Implement exponential backoff for failed HTTP requests
# ❌ DON'T: Expose internal error details to clients
# ❌ DON'T: Log sensitive information (passwords, tokens)

# =============================================================================
# 3. PROJECT STRUCTURE & ORGANIZATION
# =============================================================================

# Crawler_Practice/
# ├── core/                          # Shared crawler infrastructure
# │   ├── __init__.py
# │   ├── base_crawler.py            # BaseCrawler abstract class
# │   └── utils.py                   # Shared utilities (logging, validation)
# │
# ├── crawlers/                      # Concrete crawler implementations
# │   ├── __init__.py
# │   ├── yahoo.py                   # YahooCrawler (inherits BaseCrawler)
# │   ├── movies.py                  # MoviesCrawler
# │   ├── jobs.py                    # JobsCrawler
# │   └── ...                        # Other crawlers (follows same pattern)
# │
# ├── backend/                       # FastAPI application
# │   ├── main.py                    # FastAPI app creation + startup
# │   ├── config.py                  # Settings (env vars, constants)
# │   ├── database.py                # SQLAlchemy setup + get_db()
# │   │
# │   ├── models/
# │   │   ├── __init__.py
# │   │   ├── task.py                # TaskModel (SQLAlchemy)
# │   │   └── user.py                # UserModel (optional, Phase 2)
# │   │
# │   ├── schemas/
# │   │   ├── __init__.py
# │   │   ├── task.py                # TaskCreate, TaskResponse (Pydantic)
# │   │   └── crawler.py             # CrawlerRequest, CrawlerResponse
# │   │
# │   ├── services/
# │   │   ├── __init__.py
# │   │   ├── crawler_service.py     # Business logic for crawlers
# │   │   └── task_service.py        # Business logic for tasks
# │   │
# │   ├── crud/
# │   │   ├── __init__.py
# │   │   └── task.py                # CRUD operations for Task model
# │   │
# │   ├── routers/
# │   │   ├── __init__.py
# │   │   ├── crawlers.py            # GET /crawlers, POST /run
# │   │   ├── tasks.py               # GET /tasks/{id}, GET /tasks
# │   │   └── websocket.py           # WS /ws/crawler/{task_id}
# │   │
# │   ├── requirements.txt           # Dependencies
# │   └── Dockerfile                 # Container image
# │
# ├── frontend/                      # React + TypeScript application
# │   ├── src/
# │   │   ├── App.tsx                # Root component
# │   │   ├── main.tsx               # Entry point
# │   │   │
# │   │   ├── components/
# │   │   │   ├── CrawlerPanel.tsx   # Crawler selection + run button
# │   │   │   ├── TaskCard.tsx       # Display single task status
# │   │   │   └── ProgressBar.tsx    # Reusable progress indicator
# │   │   │
# │   │   ├── pages/
# │   │   │   ├── Dashboard.tsx      # Main dashboard page
# │   │   │   └── History.tsx        # Task history (Phase 2)
# │   │   │
# │   │   ├── hooks/
# │   │   │   ├── useCrawler.ts      # Hook for running crawlers
# │   │   │   ├── useWebSocket.ts    # Hook for WebSocket connection
# │   │   │   └── useTasks.ts        # Hook for task management
# │   │   │
# │   │   ├── services/
# │   │   │   └── api.ts             # Fetch/axios wrapper
# │   │   │
# │   │   ├── types/
# │   │   │   └── index.ts           # TypeScript interfaces (Task, Crawler)
# │   │   │
# │   │   └── styles/
# │   │       └── App.css
# │   │
# │   ├── public/
# │   ├── vite.config.ts
# │   ├── tsconfig.json
# │   └── package.json
# │
# ├── outputs/                       # Crawler output artifacts
# │   ├── yahoo/                     # Yahoo Finance results
# │   ├── movies/                    # Movie data
# │   └── ...
# │
# ├── tests/                         # Unit and integration tests
# │   ├── test_crawler_api.py
# │   ├── test_websocket.py
# │   └── conftest.py                # pytest fixtures
# │
# ├── docker-compose.yml             # Multi-container orchestration
# ├── .env.example                   # Environment template
# ├── .gitignore
# ├── README.md
# └── 2month_roadmap.md              # Learning path reference

# =============================================================================
# 4. API RESPONSE FORMAT SPECIFICATION
# =============================================================================

## Success Response (HTTP 200, 201, 202):
# {
#   "status": "success",
#   "data": {
#     "task_id": "uuid-123",
#     "crawler": "yahoo",
#     "progress": 45,
#     "status": "running"
#   },
#   "timestamp": "2026-01-07T12:00:00Z"
# }

## Error Response (HTTP 400, 401, 403, 404, 500):
# {
#   "status": "error",
#   "error": {
#     "code": "INVALID_CRAWLER",
#     "message": "Unknown crawler type: invalid",
#     "details": null
#   },
#   "timestamp": "2026-01-07T12:00:00Z"
# }

## WebSocket Message Format:
# {
#   "task_id": "uuid-123",
#   "status": "running",
#   "progress": 75,
#   "message": "Processing page 3 of 5"
# }

# =============================================================================
# 5. AGENT BEHAVIOR & DECISION TREES
# =============================================================================

## When user asks for "Crawler" code:
# ├─ Is it generic (reusable across crawlers)?
# │  └─ YES → Create in /core/base_crawler.py or extend BaseCrawler
# └─ NO (specific to one crawler)?
#    └─ YES → Create in /crawlers/{crawler_name}.py

## When user asks for "API" or "Route" code:
# ├─ Check if error handling is needed (YES, always)
# ├─ Check if Pydantic validation is needed (YES, always)
# ├─ Check if async is used (YES, mandatory)
# ├─ Check if database access needed (use get_db dependency)
# └─ Return proper HTTP status codes

## When user asks to "refactor":
# ├─ Verify change doesn't break BaseCrawler contract
# ├─ Check if tests still pass
# ├─ Ensure no synchronous code in async context
# └─ Update docstrings if logic changes

## When migrating from sync to async:
# ├─ Replace 'requests' with 'httpx'
# ├─ Add 'async' to function definitions
# ├─ Add 'await' to I/O operations
# ├─ Use 'asyncio.gather()' for parallel tasks
# └─ Explain the benefit: "Non-blocking I/O allows handling multiple requests"

## When suggesting code:
# ├─ Is Phase context correct? (Don't suggest Celery in Phase 1)
# ├─ Does it match the roadmap? (Check 2month_roadmap.md)
# ├─ Is it production-ready? (Error handling, logging, types)
# └─ Is it tested? (Unit tests or example test case)

# =============================================================================
# 6. ROADMAP CONTEXT & PHASES
# =============================================================================

## Current Phase: PHASE 1 (Days 1-14) - FastAPI + Async Basics
# Goals:
# - ✅ Master Python async/await (asyncio.gather, asyncio.create_task)
# - ✅ Setup FastAPI skeleton with proper structure
# - ✅ Integrate 6 existing crawlers with async wrappers
# - ✅ Implement WebSocket real-time progress
# - ✅ Setup JWT authentication
# - ✅ Write basic tests

# DO:
# - Focus on async/await understanding
# - Convert sync crawlers to async wrappers (asyncio.to_thread)
# - Use BackgroundTasks for long-running jobs
# - Build complete API documentation (/docs)

# DON'T:
# - Don't start React coding yet (Phase 3)
# - Don't add Celery yet (Phase 2)
# - Don't use Postgres yet (Phase 2)
# - Don't over-engineer; simple is better

## Next Phase: PHASE 2 (Days 15-28) - Production Deployment
# - Database migration (SQLite → Postgres)
# - Task queue (BackgroundTasks → Celery + Redis)
# - Docker containerization
# - Error handling improvements

## Final Phase: PHASE 3 (Days 29+) - React Frontend
# - React component development
# - WebSocket integration in React
# - Real-time UI updates
# - Task history and visualization

# =============================================================================
# 7. SECURITY & ENVIRONMENT VARIABLES
# =============================================================================

# Required .env variables:
# DATABASE_URL=sqlite:///./crawler_tasks.db
# SECRET_KEY=your-secret-key-change-in-production
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# REDIS_URL=redis://localhost:6379/0 (Phase 2)

# Security Rules:
# ✅ DO: Use os.getenv() for all configuration
# ✅ DO: Never commit .env file (add to .gitignore)
# ✅ DO: Use HTTPS in production (FastAPI + SSL certificate)
# ✅ DO: Validate all user input with Pydantic
# ❌ DON'T: Log sensitive data (tokens, passwords, API keys)
# ❌ DON'T: Expose internal error messages to clients

# =============================================================================
# 8. TESTING STANDARDS
# =============================================================================

# Test Framework: pytest
# Coverage Target: >80% for critical paths

# Test Categories:
# 1. Unit Tests: Individual functions (crawler logic, validation)
#    - Use pytest fixtures for setup/teardown
#    - Mock external API calls
#    - Example: test_fetch_stock_valid_symbol()

# 2. Integration Tests: API endpoints + database
#    - Use TestClient from fastapi
#    - Test full request-response cycle
#    - Example: test_run_crawler_endpoint()

# 3. WebSocket Tests: Real-time communication
#    - Test connection, message sending, disconnection
#    - Example: test_websocket_receive_progress()

# Test Execution:
# - Run locally: pytest tests/ -v
# - With coverage: pytest --cov=backend tests/
# - Mock external calls: from unittest.mock import patch

# =============================================================================
# 9. PERFORMANCE & OPTIMIZATION (Phase 2+)
# =============================================================================

# Async Performance:
# ✅ Use asyncio.gather() for parallel tasks (5-10x faster than sequential)
# ✅ Use connection pooling for HTTP (httpx.AsyncClient)
# ✅ Cache frequently accessed data (in-memory or Redis)
# ✅ Implement request timeouts (httpx with timeout=10)

# Database Performance:
# ✅ Index frequently queried columns (crawler_type, status, created_at)
# ✅ Paginate list endpoints (limit, offset parameters)
# ✅ Use lazy loading for relationships

# Frontend Performance:
# ✅ Use React.memo for expensive components
# ✅ Defer non-critical renders (useDeferredValue)
# ✅ Implement virtual scrolling for long lists (Phase 2)

# =============================================================================
# 10. TROUBLESHOOTING & COMMON PATTERNS
# =============================================================================

## Pattern: Running sync code in async context
# Problem: crawler.run() is synchronous, but route is async
# Solution: Use asyncio.to_thread(crawler.run)
# Code:
#   result = await asyncio.to_thread(crawler.run)

## Pattern: Handling WebSocket disconnections
# Problem: Client disconnects, server hangs
# Solution: Wrap in try/except with proper cleanup
# Code:
#   try:
#       while True:
#           data = await websocket.receive_json()
#   except WebSocketDisconnect:
#       manager.disconnect(websocket)

## Pattern: Exponential backoff for failed requests
# Problem: Network timeouts, need retry logic
# Solution: Use tenacity library or custom retry decorator
# Code:
#   from tenacity import retry, wait_exponential, stop_after_attempt
#   @retry(wait=wait_exponential(multiplier=1, min=2, max=10), 
#          stop=stop_after_attempt(3))
#   async def fetch_with_retry():
#       ...

# =============================================================================
# 11. GIT COMMIT CONVENTIONS
# =============================================================================

# Commit message format:
# [Phase 1] feat: Add FastAPI skeleton with crawlers integration
# [Phase 1] fix: Handle WebSocket disconnect properly
# [Phase 1] test: Add 80% coverage for crawler service
# [Phase 2] chore: Setup SQLAlchemy and migrations

# Branch naming:
# feature/phase1-fastapi-setup
# fix/websocket-disconnect-bug
# docs/add-api-documentation

# =============================================================================
# END OF CURSOR RULES
# =============================================================================
# Last Updated: 2026-01-07
# Related: 2month_roadmap.md
# Contact: Ask for clarification on any rule
