# Deployment Guide (Vercel + Render)

This guide targets a portfolio-friendly public deployment:
- `frontend` on Vercel
- `backend` + PostgreSQL + Redis on Render

## 1. Prerequisites

- GitHub repository is up to date.
- You can run local checks:
  - `cd frontend && npm run build`
  - `docker compose build backend`
- Prepare a strong `SECRET_KEY`.

## 2. Deploy Backend to Render

1. Sign in to Render and create a new **Blueprint** service.
2. Select this repository root and use `render.yaml`.
3. After resources are created, open `crawler-backend` env vars and set:
   - `SECRET_KEY` (required)
   - `CORS_ORIGINS` (required, set to your Vercel domain JSON array)
   - `FIRECRAWL_API_KEY` (optional)
4. Trigger deploy and wait for healthy status.
5. Verify:
   - `GET https://<your-backend-domain>/health`
   - `GET https://<your-backend-domain>/docs`

## 3. Deploy Frontend to Vercel

1. Import repository into Vercel.
2. Set project root to `frontend`.
3. Add environment variables:
   - `VITE_API_BASE_URL=https://<your-backend-domain>/api`
   - `VITE_WS_BASE_URL=wss://<your-backend-domain>`
4. Keep `frontend/vercel.json` as default config.
5. Deploy and verify login/registration page is reachable.

## 4. Production Smoke Test

Run through this checklist:

1. Register user and login.
2. Open dashboard and fetch crawler list.
3. Start a crawler task and confirm task row is created.
4. Confirm WebSocket progress updates on task detail card.
5. Open history page and verify task persistence after refresh.

## 5. Common Issues

- **CORS 403 / blocked request**
  - `CORS_ORIGINS` must be valid JSON array, e.g. `["https://your-app.vercel.app"]`.
- **WebSocket cannot connect**
  - `VITE_WS_BASE_URL` must be `wss://` in production.
- **Auth works locally but not online**
  - Check `VITE_API_BASE_URL` includes `/api` suffix.
- **Task execution unstable**
  - Keep `USE_CELERY=false` for MVP; add worker rollout after baseline is stable.
