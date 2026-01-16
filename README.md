# 🚀 爬虫管理平台 (Crawler Management Platform)

一个基于 **FastAPI + React + TypeScript** 的全栈异步爬虫管理系统，支持统一调度、任务追踪与实时进度展示。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2.2-blue.svg)](https://www.typescriptlang.org/)

## ✨ 亮点能力

- **异步任务管理**：后台任务队列 + 状态跟踪
- **实时进度**：WebSocket 推送任务进度
- **统一爬虫框架**：BaseCrawler 规范化接入
- **安全认证**：JWT 登录与权限控制
- **可部署**：Docker + PostgreSQL + Redis
- **前后端分离**：React + TypeScript + Vite

## 🧩 技术栈

- 后端：FastAPI、SQLAlchemy (Async)、JWT、Celery、Redis、PostgreSQL
- 前端：React 18、TypeScript、Vite、Tailwind CSS
- 部署：Docker / Docker Compose

## 🏗️ 架构概览

- **Frontend**：任务列表 / 进度看板 / 认证
- **Backend**：Router → Service → CRUD → Model
- **Worker**：Celery 执行爬虫任务
- **Storage**：PostgreSQL / SQLite
- **Realtime**：WebSocket 进度通道

## 📁 目录结构

```
backend/    # FastAPI 后端
frontend/   # React 前端
tests/      # 测试
docs/       # 文档
legacy/     # 早期实验代码（已归档）
```

## 🚀 快速开始

### 方式 1：Docker（推荐）

```bash
git clone <your-repo-url>
cd Crawler_Practice

# 创建并编辑 .env（参考 docs/env.example.txt）
# 至少设置：SECRET_KEY / POSTGRES_* / ADMIN_*

docker compose up --build
```

### 方式 2：本地开发

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

### 初始化管理员

```bash
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
- 所有敏感配置通过环境变量注入
- `legacy/` 为历史实验代码，已移除数据输出文件

## 📄 License

MIT License
