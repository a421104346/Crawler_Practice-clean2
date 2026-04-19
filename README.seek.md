# Crawler Management Platform

## 60-Second Pitch

Production-oriented crawler orchestration platform built with FastAPI + React, supporting authenticated task execution, real-time WebSocket progress, and admin-level operations in one unified dashboard.

## Why This Project

Before this project, crawler scripts were isolated and hard to operate: no unified API, no role control, and no consistent task visibility.  
I turned that into a deployable full-stack system with a standard task lifecycle and centralized monitoring.

## What I Built

- Unified crawler registry and execution APIs
- Async task lifecycle tracking: `pending -> running -> completed/failed`
- JWT authentication + role-based access (user/admin)
- Task-scoped real-time updates via `WS /ws/tasks/{task_id}`
- Health and metrics endpoints for operational visibility

## My Role

- Designed backend architecture (`Router -> Service -> CRUD -> Model`)
- Implemented auth flows and protected routes
- Built task APIs + persistence model
- Integrated multiple crawler adapters behind one service contract
- Developed frontend pages for auth, dashboard, and history
- Added Dockerized deployment configs and test scaffolding

## Stack

- Backend: FastAPI, SQLAlchemy Async, Pydantic v2, JWT (python-jose), Alembic
- Frontend: React 18, TypeScript, Vite, Zustand, React Query
- Infra: Docker, PostgreSQL, Redis/Celery (optional), WebSocket

## Representative APIs

- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `GET /api/crawlers`, `POST /api/crawlers/{crawler_type}/run`
- `GET /api/tasks`, `GET /api/tasks/{task_id}`, `DELETE /api/tasks/{task_id}`
- `GET /api/monitoring/health`, `GET /api/monitoring/stats`
- `WS /ws/tasks/{task_id}`

## Crawler Coverage

- Yahoo Finance quotes
- Douban Top250 movies
- Remotive jobs
- Weibo hot search (Playwright)
- Xiaohongshu discovery (Playwright)
- ProSettings extraction

## Quantified Impact (Fill Before Publishing)

- Reduced manual crawler run-and-check steps by **XX%**
- Improved task status visibility from **none** to **real-time**
- Reduced issue triage time by **XX%** via centralized logs + task records
- Increased successful run rate to **XX%** in the demo environment

## Demo Assets Checklist

Prepare these before sharing portfolio links:

1. Dashboard screenshot (crawler list + task cards)
2. Task execution screenshot (running state + progress)
3. History/monitoring screenshot (stats + status distribution)
4. 2-3 minute walkthrough video (login -> run task -> observe progress -> download result)

## Deployment Readiness

- Backend Docker build verified
- Frontend production build verified
- Cloud deployment templates included (`render.yaml`, `frontend/vercel.json`)
- Deployment runbook available at `docs/deploy-vercel-render.md`