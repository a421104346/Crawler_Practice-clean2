# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Crawler Management Platform: FastAPI backend (port 8000) + React/Vite frontend (port 3000) + SQLite. See `README.md` for full API docs, project structure, and Docker options.

### Critical: Environment Variable Override

The Cloud VM may inject environment variables (e.g. `DATABASE_URL`, `USE_CELERY`, `POSTGRES_URL`) from repo secrets that override `.env` file values. When starting the backend locally with SQLite, you **must** override them inline:

```bash
DATABASE_URL="sqlite+aiosqlite:///./backend/data/crawler_tasks.db" \
USE_CELERY=false \
POSTGRES_URL="" \
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload \
  --reload-exclude "logs/*" --reload-exclude "data/*.db" --reload-exclude "__pycache__/*"
```

### Starting Services

- **Backend**: Use the command above from `/workspace`. SQLite DB auto-creates at `backend/data/crawler_tasks.db`.
- **Frontend**: `cd frontend && npm run dev` (port 3000, proxies `/api` and `/ws` to backend).

### Key Gotchas

- `passlib[bcrypt]` requires `bcrypt==4.0.1` (not 5.x) due to a compatibility bug. The update script pins this.
- Missing pip deps not in `requirements.txt`: `beautifulsoup4`, `lxml`, `email-validator`. The update script installs these.
- Hot reload does **not** detect `pip install` changes; restart uvicorn after installing new packages.
- The uvicorn CLI flag is `--reload-exclude` (singular), not `--reload-excludes`.

### Testing

- Backend tests: `pytest tests/ -v --ignore=tests/test_yahoo_manual.py` (that file has a pre-existing broken import).
- Frontend lint: `cd frontend && npx eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0` (pre-existing warnings/errors exist).
- Frontend build: `cd frontend && npx tsc && npx vite build`.

### Admin Bootstrap

After starting the backend, run `python3 create_admin.py` to create an admin user (reads `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` from env).
