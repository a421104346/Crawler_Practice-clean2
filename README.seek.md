# Crawler Management Platform
## Project Snapshot

- **Project type**: Full-stack web application for crawler orchestration and task management
- **Role**: Full-stack developer (backend-focused)
- **Stack**: FastAPI, Python, SQLAlchemy (async), React, TypeScript, WebSocket, JWT, Docker, Redis/Celery (optional)
- **Core value**: Unified management for multiple crawlers with real-time progress and role-based access control

## One-Line Pitch

Built a production-oriented crawler management platform that supports authenticated task execution, real-time progress streaming, and admin operations through a modern FastAPI + React architecture.

## Problem & Solution

### Problem

Crawler scripts were isolated, hard to monitor, and lacked a consistent execution and permission model.

### Solution

Designed and implemented a centralized platform with:

- Unified crawler registry and execution APIs
- Async task lifecycle management (`pending/running/completed/failed`)
- JWT authentication and admin/user role boundaries
- WebSocket-based real-time task progress updates
- Monitoring endpoints for health, metrics, and operational visibility

## My Responsibilities

- Designed backend architecture (Router -> Service -> CRUD -> Model)
- Implemented authentication and authorization flows
- Built task APIs and persistence model for lifecycle tracking
- Integrated multiple crawlers behind a standardized service interface
- Added WebSocket channel for real-time task status delivery
- Built/maintained frontend pages for user and admin workflows
- Added Docker-based deployment configuration and test suite

## Technical Highlights

- **Asynchronous backend**: FastAPI + async SQLAlchemy session pattern
- **Realtime communication**: task-scoped WebSocket channel (`/ws/tasks/{task_id}`)
- **Security**: JWT token issuance/validation, role-based protected routes
- **Scalable execution path**: default BackgroundTasks with optional Celery + Redis mode
- **Observability**: health checks, detailed dependency checks, metrics endpoints
- **Extensible crawler design**: single service managing multiple crawler adapters

## Business/Engineering Impact

Use or adjust the numbers below to match your final evidence before publishing:

- Reduced manual crawler run-and-check workflow by **~XX%**
- Improved task tracking transparency from “no visibility” to **real-time status and progress**
- Decreased debugging time via centralized logs/monitoring and task records
- Enabled multi-user operation with clear access boundaries (user vs admin)

## Built-in Crawler Coverage

- Yahoo Finance quotes
- Douban Top250 movies
- Remotive jobs
- Weibo hot search (Playwright)
- Xiaohongshu discovery (Playwright)
- ProSettings data extraction

## API Surface (Representative)

- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `GET /api/crawlers`, `POST /api/crawlers/{crawler_type}/run`
- `GET /api/tasks`, `GET /api/tasks/{task_id}`, `DELETE /api/tasks/{task_id}`
- `WS /ws/tasks/{task_id}`
- `GET /api/monitoring/health`, `GET /api/monitoring/stats`

## Deployment & Ops

- Local development with Python + Node.js
- Containerized deployment via Docker Compose
- Optional distributed task execution via Celery + Redis
- Environment-driven configuration (`.env`) for secrets and runtime settings

## Testing

- `pytest`-based backend test suite
- API/auth/task/firecrawl coverage included
- Integration tests for crawler flows (network-dependent)