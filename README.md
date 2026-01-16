# 🚀 爬虫管理平台 (Crawler Management Platform)

基于 **FastAPI + React + TypeScript** 的全栈异步爬虫管理系统，提供统一调度、任务追踪、权限认证与实时进度展示。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2.2-blue.svg)](https://www.typescriptlang.org/)

## ✨ 核心特性

- **异步任务执行**：后台任务与状态跟踪（Phase 1 默认 BackgroundTasks）
- **实时进度推送**：WebSocket 任务进度消息
- **统一爬虫框架**：`BaseCrawler` 规范化接入
- **JWT 认证**：登录、鉴权与权限控制
- **前后端分离**：React + TypeScript + Vite
- **可部署**：Docker / Docker Compose（PostgreSQL + Redis 可选）

## 📝 功能简介

- 统一管理多个爬虫任务的创建、运行与状态查询
- 任务进度通过 WebSocket 实时推送到前端界面
- 支持用户注册、登录与 JWT 鉴权访问 API
- 任务结果输出到 `outputs/`，便于后续处理与归档

## ✅ 功能清单

- **认证与权限**：注册、登录、JWT 鉴权、管理员权限
- **爬虫管理**：爬虫列表、详情查看、启动爬虫任务
- **任务中心**：任务创建、列表分页、状态/进度查询、取消/删除
- **实时通道**：WebSocket 推送任务进度与结果
- **监控与统计**：健康检查、系统指标、任务统计
- **前端界面**：任务面板、认证页、实时进度展示

## 🧭 API 概览

### 认证 / 用户

- `POST /api/auth/register` 注册
- `POST /api/auth/login` 登录
- `GET /api/auth/me` 当前用户信息
- `POST /api/auth/logout` 登出

### 爬虫

- `GET /api/crawlers` 获取爬虫列表
- `GET /api/crawlers/{crawler_type}` 获取爬虫详情
- `POST /api/crawlers/{crawler_type}/run` 启动爬虫任务

### 任务

- `GET /api/tasks` 任务列表（分页/过滤）
- `GET /api/tasks/{task_id}` 任务详情
- `PATCH /api/tasks/{task_id}` 更新任务（如取消）
- `DELETE /api/tasks/{task_id}` 删除任务

### WebSocket

- `WS /ws/tasks/{task_id}` 订阅指定任务进度

### 管理员

- `GET /api/admin/users` 用户列表
- `DELETE /api/admin/users/{user_id}` 删除用户
- `GET /api/admin/tasks` 管理员任务列表
- `DELETE /api/admin/tasks/{task_id}` 删除任务

### 监控

- `GET /api/monitoring/health` 基础健康检查
- `GET /api/monitoring/health/detailed` 详细健康检查
- `GET /api/monitoring/metrics` 系统指标（管理员）
- `GET /api/monitoring/stats` 任务统计

## 🧩 技术栈

- 后端：FastAPI、SQLAlchemy (Async)、Pydantic v2、JWT、httpx
- 前端：React 18、TypeScript、Vite、Tailwind CSS
- 数据库：SQLite（默认）/ PostgreSQL（可选）
- 任务队列：BackgroundTasks（默认）/ Celery + Redis（可选）

## 🏗️ 架构概览

- **Frontend**：任务面板 / 登录注册 / 进度展示
- **Backend**：Router → Service → CRUD → Model
- **Realtime**：WebSocket 推送任务进度
- **Storage**：SQLite（本地）或 PostgreSQL（部署）

## 📁 目录结构

```
backend/    # FastAPI 后端
frontend/   # React 前端
tests/      # 测试
docs/       # 文档与阶段说明
legacy/     # 历史实验代码（归档）
outputs/    # 爬虫输出目录（默认为空）
```

## 🚀 快速开始

### 方式 1：本地开发（推荐）

```bash
# 后端
cd backend
pip install -r requirements.txt
python main.py

# 前端
cd ../frontend
npm install
npm run dev
```

后端默认地址：`http://localhost:8000`  
前端默认地址：`http://localhost:5173`

### 方式 2：Docker（可选）

```bash
git clone <your-repo-url>
cd Crawler_Practice-clean2

# 创建并编辑 .env（参考 docs/env.example.txt）
# 至少设置：SECRET_KEY / POSTGRES_* / ADMIN_*

docker compose up --build
```

### 初始化管理员（PowerShell）

```powershell
# 设置管理员环境变量后再执行
set ADMIN_USERNAME=admin
set ADMIN_EMAIL=admin@example.com
set ADMIN_PASSWORD=YOUR_PASSWORD

python create_admin.py
```

## 🧪 测试

```bash
pytest tests/ -v
```

## 🔐 安全与公开说明

- 仓库不包含任何真实密钥与日志
- 敏感配置通过环境变量注入（勿提交 `.env`）
- `legacy/` 为历史实验代码，已清理输出文件

## 📄 License

MIT License
