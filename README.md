# Crawler Management Platform

A full-stack crawler management system built with **FastAPI + React + TypeScript**.
It provides crawler orchestration, task tracking, JWT authentication, and real-time progress updates via WebSocket.

For a recruiter-focused summary, see `README.seek.md`.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2.2-blue.svg)](https://www.typescriptlang.org/)

## Features

- Unified crawler registry and execution service
- Async task execution (FastAPI `BackgroundTasks`, optional Celery mode)
- Real-time task progress streaming with WebSocket
- JWT-based auth (register/login/me/logout) and admin endpoints
- Monitoring APIs (health checks, metrics, task stats)
- Built-in Firecrawl integration for scraping endpoints
- React dashboard for user/admin workflows

## Built-in Crawlers

The backend currently registers these crawler types:

- `yahoo` - Yahoo Finance quote data (requires `symbol`)
- `movies` - Douban Top250 movie list
- `jobs` - Remotive remote job data
- `weibo` - Weibo hot search crawler (Playwright-based)
- `rednote` - Xiaohongshu discovery crawler (Playwright-based)
- `prosettings` - CS2 pro player settings crawler

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy Async, Pydantic v2, python-jose (JWT), Alembic
- **Frontend**: React 18, TypeScript, Vite, Zustand, React Query
- **Database**: SQLite by default, PostgreSQL supported
- **Queue/Worker**: FastAPI BackgroundTasks by default, optional Celery + Redis
- **Other**: WebSocket, Playwright, Firecrawl API integration

## Project Structure

```text
backend/              FastAPI backend
  crawlers/           concrete crawler implementations
  core/               shared crawler base class
  routers/            API routes (auth, tasks, crawlers, admin, monitoring, firecrawl, websocket)
  services/           business logic layer
  models/             SQLAlchemy models
  schemas/            Pydantic schemas
frontend/             React + TypeScript frontend
tests/                pytest test suite
docs/env.example.txt  example environment variables
docker-compose.yml    production-like compose stack
docker-compose.dev.yml development compose stack
create_admin.py       admin bootstrap script
```

## Quick Start (Local Development)

### 1) Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend default URL: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

> Optional for Playwright-based crawlers (`weibo`, `rednote`):
>
> ```bash
> python -m playwright install chromium
> ```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:5173`

## Environment Variables

1. Create `.env` at the project root.
2. Use `docs/env.example.txt` as the template.

Common keys:

- `SECRET_KEY`
- `DATABASE_URL` / `POSTGRES_URL`
- `REDIS_URL`
- `USE_CELERY`
- `FIRECRAWL_API_KEY`
- `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`

## Admin Bootstrap

After setting admin env vars, run:

```bash
python create_admin.py
```

This script creates the admin user (or resets password/promotes to admin if the user already exists).

## API Overview

### Public

- `GET /`
- `GET /health`
- `GET /api/crawlers`
- `GET /api/crawlers/{crawler_type}`
- `GET /api/monitoring/health`
- `GET /api/monitoring/health/detailed`
- `GET /api/monitoring/stats`

### Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`

### Task/Crawler APIs

- `POST /api/crawlers/{crawler_type}/run` (auth required)
- `GET /api/tasks` (auth required)
- `GET /api/tasks/{task_id}` (auth required)
- `DELETE /api/tasks/{task_id}` (auth required)
- `PATCH /api/tasks/{task_id}` (currently open in code)

### Realtime

- `WS /ws/tasks/{task_id}`

### Admin (Admin Role Required)

- `GET /api/admin/users`
- `DELETE /api/admin/users/{user_id}`
- `GET /api/admin/tasks`
- `DELETE /api/admin/tasks/{task_id}`
- `GET /api/monitoring/metrics`

### Firecrawl (Authenticated)

- `POST /api/firecrawl/scrape`
- `POST /api/firecrawl/weibo/hot-rank1`

## Docker

### Production-like stack

```bash
docker compose up --build
```

Includes PostgreSQL, Redis, backend, Celery worker/beat, and Flower.

### Development stack

```bash
docker compose -f docker-compose.dev.yml up --build
```

## Testing

Run from project root:

```bash
pytest tests/ -v
```

Some integration tests require network access and are marked as slow.

## License

MIT
