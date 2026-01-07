# Project: Crawler Management Platform (FastAPI + React)
# Goal: Build a production-grade, asynchronous crawler system with a modern Web UI.

# -----------------------------------------------------------------------------
# 1. Technology Stack & Constraints
# -----------------------------------------------------------------------------
# Backend:
# - Framework: FastAPI (Async is MANDATORY)
# - Validation: Pydantic v2
# - Database: SQLAlchemy (AsyncSession) or SQLite for prototyping
# - Task Queue: BackgroundTasks (Phase 1) -> Celery + Redis (Phase 2)
# - Networking: httpx (Async) instead of requests (Sync) - IMPORTANT!

# Frontend:
# - Framework: React (Latest)
# - Language: TypeScript (Strict mode)
# - State Management: React Context or Zustand
# - Styling: Tailwind CSS or plain CSS modules
# - Communication: fetch / axios + WebSocket for real-time updates

# -----------------------------------------------------------------------------
# 2. Coding Standards
# -----------------------------------------------------------------------------
# General:
# - Type Hints: MANDATORY for all Python functions (args and return types).
# - Docstrings: Google style docstrings for complex logic.
# - Error Handling: Use try/except blocks with specific exceptions. Never bare 'except:'.
# - Logging: Use the 'logging' module, never 'print' in backend code.

# Python / FastAPI:
# - Use 'async def' for all route handlers and I/O bound functions.
# - Use 'await' for database queries and HTTP requests.
# - Pydantic models must be defined for all request bodies and response schemas.
# - Separation of Concerns: Routes -> Services -> CRUD -> Models.

# TypeScript / React:
# - Functional Components only (Hooks).
# - Interfaces/Types for all props and state.
# - No 'any' type unless absolutely necessary.
# - Use 'useEffect' carefully to avoid infinite loops.

# -----------------------------------------------------------------------------
# 3. Project Structure
# -----------------------------------------------------------------------------
# /core        -> Shared crawler logic (BaseCrawler, Utils). Independent of FastAPI.
# /crawlers    -> Specific crawler implementations (Yahoo, Movies, etc.). Inherit from BaseCrawler.
# /backend     -> FastAPI application (main.py, routers/, models/, services/).
# /frontend    -> React application (src/, public/).
# /outputs     -> Directory for crawler artifacts (CSV, JSON, Images).

# -----------------------------------------------------------------------------
# 4. Agent Behavior Guidelines
# -----------------------------------------------------------------------------
# - When user asks for "Crawler" code: Check if it should be in '/core' (generic) or '/crawlers' (specific).
# - When user asks for "API" code: Ensure it handles errors (404, 500) and returns JSON.
# - When refactoring: Always verify if the change breaks the 'BaseCrawler' contract.
# - Security: Never hardcode API keys or secrets. Use env vars (os.getenv).
# - If switching from 'requests' (sync) to 'httpx' (async), explain the difference briefly.

# -----------------------------------------------------------------------------
# 5. Roadmap Context (Current Focus)
# -----------------------------------------------------------------------------
# We are following '2month_roadmap.md'.
# Current Phase: Phase 1 (FastAPI + Async Basics).
# - Focus on converting synchronous 'requests' code to asynchronous 'httpx' or 'asyncio'.
# - Setting up the FastAPI skeleton.
# - Do NOT suggest React code until Phase 3 (Frontend) is reached.

