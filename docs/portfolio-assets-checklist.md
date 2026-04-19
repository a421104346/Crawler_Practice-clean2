# Portfolio Assets Checklist

Use this checklist to package the project for recruiters quickly.

## 1) Public Links

- [ ] Frontend demo URL
- [ ] Backend API docs URL (`/docs`)
- [ ] GitHub repository URL

## 2) Screenshots (Recommended 3-5)

- [ ] Login/Register page
- [ ] Dashboard with crawler selection
- [ ] Task running state with WebSocket progress
- [ ] Task history/statistics panel
- [ ] Optional admin page (user/task management)

Naming suggestion:
- `01-login.png`
- `02-dashboard.png`
- `03-task-running.png`
- `04-history.png`
- `05-admin.png`

## 3) Demo Video (2-3 Minutes)

Suggested script:

1. Project intro (10-15s): problem and value
2. Login and start task (30-40s)
3. Show real-time updates (30-40s)
4. Show completed result and history (30-40s)
5. Mention architecture and deployment (20-30s)

## 4) Resume Bullet Templates

- Built a full-stack crawler orchestration platform with FastAPI + React, supporting authenticated task execution and real-time progress streaming over WebSocket.
- Designed a layered backend architecture (`Router -> Service -> CRUD -> Model`) and standardized multiple crawler adapters under a unified API contract.
- Shipped deployment-ready infrastructure with Docker and cloud templates, enabling portfolio-grade public demos.

## 5) Metrics to Collect Before Publishing

- [ ] End-to-end task success rate
- [ ] Average task completion time by crawler type
- [ ] API response latency for key endpoints (`/api/tasks`, `/api/crawlers`)
- [ ] Daily/weekly run count in demo environment

## 6) Final Quality Gate

- [ ] `npm run build` passes
- [ ] Backend tests pass in CI
- [ ] Secrets are not committed
- [ ] README and README.seek include live demo links
