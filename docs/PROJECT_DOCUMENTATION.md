# Full-Stack Crawler Management Platform Documentation

This document consolidates the project's technical architecture, deployment guide, development guidelines, and milestone summaries, providing a comprehensive reference for developers.

---

## 📚 Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Quick Start](#3-quick-start)
4. [Features & API](#4-features--api)
5. [Development Guidelines](#5-development-guidelines)
6. [Deployment](#6-deployment)
7. [Roadmap & Phases](#7-roadmap--phases)

---

## 1. Overview

### Introduction
This project is a full-stack asynchronous crawler management platform built with **FastAPI + React + TypeScript**, designed to provide unified crawler task scheduling, real-time status tracking, and permission management. It is suitable for scenarios requiring centralized management of multiple crawler scripts, monitoring execution progress, and archiving results.

### Core Features
- **Async Tasks**: Supports background task queues (BackgroundTasks / Celery) for non-blocking crawling.
- **Real-time Progress**: Pushes task logs and progress bars in real time via WebSocket.
- **Permission Management**: Integrates JWT authentication with role-based access control for regular users and administrators.
- **Extensibility**: Based on the `BaseCrawler` abstract class, making it easy to integrate new crawlers.
- **Modern Frontend**: React 18 + Tailwind CSS, providing an intuitive task dashboard.

---

## 2. Architecture

### Tech Stack
| Domain | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+, FastAPI | Async web framework, high-performance API |
| **Database** | SQLite (Dev) / PostgreSQL (Prod) | Using SQLAlchemy + Asyncpg async driver |
| **Frontend** | React 18, TypeScript, Vite | Modern SPA development experience |
| **Task Queue** | BackgroundTasks / Celery + Redis | Flexible switch between lightweight and distributed queues |
| **HTTP Requests** | httpx | Pure async HTTP client |
| **Deployment** | Docker, Docker Compose | Containerized one-click deployment |

### System Architecture Diagram
```mermaid
graph TD
    User[User (React Frontend)] -->|HTTP/WebSocket| API[FastAPI Backend]
    API -->|CRUD| DB[(PostgreSQL/SQLite)]
    API -->|Push| WS[WebSocket Manager]
    API -->|Dispatch| Queue[Task Queue (Celery/BgTasks)]
    
    subgraph "Worker Layer"
    Queue -->|Execute| Crawler[BaseCrawler Implementation]
    Crawler -->|Fetch| Target[Target Website]
    Crawler -->|Update Progress| API
    end
```

---

## 3. Quick Start

### Requirements
- Python 3.10+
- Node.js 18+
- Docker (optional)

### Local Development Setup

#### 1. Start Backend
```bash
cd backend
# Create virtual environment (optional)
python -m venv venv
# Activate: Windows: .\venv\Scripts\activate | Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database and admin
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=admin
python create_admin.py

# Start server
python main.py
# Visit: http://localhost:8000/docs
```

#### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
# Visit: http://localhost:5173
```

### Docker Setup (Recommended)
```bash
# Copy environment variables
cp docs/env.example.txt .env

# Start all services
docker compose up --build
```

---

## 4. Features & API

### 4.1 Authentication Module
- **Register/Login**: JWT Token issuance and verification.
- **Access Control**: Distinguishes between regular users and administrators via `Depends(get_current_user)` dependency injection.

### 4.2 Crawler Module
- **BaseCrawler**: All crawlers inherit from `core/base_crawler.py`.
- **Unified Interface**: The `run(params)` method provides a unified entry point with parameter validation.
- **Existing Crawlers**: Yahoo Finance, Jobs, Movies, and other examples.

### 4.3 Task Management
- **Task Creation**: User submits crawler request -> generates Task ID -> enters queue.
- **Status Flow**: `pending` -> `running` -> `completed` / `failed`.
- **Progress Callback**: Crawlers internally update DB and WebSocket in real time via `progress_callback`.

### 4.4 Monitoring
- **Health Check**: `/api/monitoring/health` checks DB, Redis, and Celery connection status.
- **System Metrics**: CPU, memory, uptime statistics (admin-only).

---

## 5. Development Guidelines

### Code Style
- **Python**: Follows PEP8, uses Type Hints, Google-style Docstrings.
- **TypeScript**: Strict mode (`strict: true`), no `any`, use Interface for data structure definitions.

### Directory Structure
```
backend/
  ├── core/          # Core abstractions (BaseCrawler)
  ├── crawlers/      # Crawler implementations
  ├── routers/       # API routes
  ├── schemas/       # Pydantic models
  ├── crud/          # Database operations
  └── tasks/         # Celery/background task definitions
frontend/
  ├── src/components # UI components
  ├── src/hooks      # Custom Hooks
  └── src/services   # API client
```

### Commit Workflow
1. Branch naming: `feat/xxx`, `fix/xxx`
2. Commit message: `[Phase X] feat: message`
3. Ensure tests pass: `pytest tests/`

---

## 6. Deployment

### Production Configuration
1. **Database Migration**: Switch to PostgreSQL.
   - Update `.env`: `DATABASE_URL=postgresql+asyncpg://...`
2. **Task Queue**: Enable Celery + Redis.
   - Set `USE_CELERY=true`
3. **Reverse Proxy**: Use Nginx to proxy API and frontend static files.

### Docker Compose Orchestration
- `docker-compose.yml`: Includes Backend, Frontend (Nginx), Postgres, Redis, Celery Worker, Flower.
- **Data Persistence**: Mounted volumes ensure DB data is not lost.

---

## 7. Roadmap & Phases

### Phase 1: Async Foundation & FastAPI (Completed)
- [x] Set up FastAPI skeleton
- [x] Implement BaseCrawler with async wrapper
- [x] WebSocket real-time communication
- [x] JWT authentication system

### Phase 2: Production-Grade Enhancements (Completed)
- [x] Integrate PostgreSQL
- [x] Introduce Celery + Redis task queue
- [x] Docker containerized deployment
- [x] System monitoring and health checks

### Phase 3: Full-Stack Integration (Completed)
- [x] React frontend development
- [x] Task list and detail pages
- [x] Real-time log and progress bar components
- [x] Mobile responsive design

### Future Plans
- **Phase 4**: Distributed crawler cluster and visual reporting
- **Phase 5**: AI-assisted parsing and anti-crawling strategy integration

---

*Last updated: 2026-01-16*
