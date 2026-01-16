# 全栈爬虫管理平台文档 (Crawler Management Platform Documentation)

本文档整合了项目的技术架构、部署指南、开发规范及阶段性成果，旨在为开发者提供全方位的参考。

---

## 📚 目录 (Table of Contents)

1. [项目概览 (Overview)](#1-项目概览-overview)
2. [技术架构 (Architecture)](#2-技术架构-architecture)
3. [快速开始 (Quick Start)](#3-快速开始-quick-start)
4. [核心功能与API (Features & API)](#4-核心功能与api-features--api)
5. [开发规范 (Development Guidelines)](#5-开发规范-development-guidelines)
6. [部署指南 (Deployment)](#6-部署指南-deployment)
7. [项目路线图与阶段回顾 (Roadmap & Phases)](#7-项目路线图与阶段回顾-roadmap--phases)

---

## 1. 项目概览 (Overview)

### 简介
本项目是一个基于 **FastAPI + React + TypeScript** 的全栈异步爬虫管理平台，旨在提供统一的爬虫任务调度、实时状态追踪及权限管理能力。适用于需要集中管理多个爬虫脚本、监控执行进度并进行结果归档的场景。

### 核心特性
- **异步任务**：支持后台任务队列（BackgroundTasks / Celery），实现非阻塞爬取。
- **实时进度**：通过 WebSocket 实时推送任务日志与进度条。
- **权限管理**：集成 JWT 认证，支持普通用户与管理员权限分级。
- **可扩展性**：基于 `BaseCrawler` 抽象类，轻松接入新爬虫。
- **现代化前端**：React 18 + Tailwind CSS，提供直观的任务看板。

---

## 2. 技术架构 (Architecture)

### 技术栈
| 领域 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **后端** | Python 3.10+, FastAPI | 异步 Web 框架，高性能 API |
| **数据库** | SQLite (Dev) / PostgreSQL (Prod) | 使用 SQLAlchemy + Asyncpg 异步驱动 |
| **前端** | React 18, TypeScript, Vite | 现代化 SPA 开发体验 |
| **任务队列** | BackgroundTasks / Celery + Redis | 灵活切换轻量级与分布式队列 |
| **网络请求** | httpx | 纯异步 HTTP 客户端 |
| **部署** | Docker, Docker Compose | 容器化一键部署 |

### 系统架构图
```mermaid
graph TD
    User[用户 (React Frontend)] -->|HTTP/WebSocket| API[FastAPI Backend]
    API -->|CRUD| DB[(PostgreSQL/SQLite)]
    API -->|Push| WS[WebSocket Manager]
    API -->|Dispatch| Queue[Task Queue (Celery/BgTasks)]
    
    subgraph "Worker Layer"
    Queue -->|Execute| Crawler[BaseCrawler Implementation]
    Crawler -->|Fetch| Target[目标网站]
    Crawler -->|Update Progress| API
    end
```

---

## 3. 快速开始 (Quick Start)

### 环境要求
- Python 3.10+
- Node.js 18+
- Docker (可选)

### 本地开发启动

#### 1. 后端启动
```bash
cd backend
# 创建虚拟环境（可选）
python -m venv venv
# 激活环境: Windows: .\venv\Scripts\activate | Mac/Linux: source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库与管理员
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=admin
python create_admin.py

# 启动服务
python main.py
# 访问: http://localhost:8000/docs
```

#### 2. 前端启动
```bash
cd frontend
npm install
npm run dev
# 访问: http://localhost:5173
```

### Docker 启动 (推荐)
```bash
# 复制环境变量
cp docs/env.example.txt .env

# 启动所有服务
docker compose up --build
```

---

## 4. 核心功能与API (Features & API)

### 4.1 认证模块 (Auth)
- **注册/登录**: JWT Token 签发与验证。
- **权限控制**: 区分普通用户与管理员，通过 `Depends(get_current_user)` 注入依赖。

### 4.2 爬虫模块 (Crawlers)
- **BaseCrawler**: 所有爬虫均继承自 `core/base_crawler.py`。
- **统一接口**: `run(params)` 方法统一入口，支持参数校验。
- **已有爬虫**: Yahoo Finance, Jobs, Movies 等示例。

### 4.3 任务管理 (Tasks)
- **任务创建**: 用户提交爬虫请求 -> 生成 Task ID -> 进入队列。
- **状态流转**: `pending` -> `running` -> `completed` / `failed`。
- **进度回调**: 爬虫内部通过 `progress_callback` 实时更新 DB 与 WebSocket。

### 4.4 监控 (Monitoring)
- **健康检查**: `/api/monitoring/health` 检查 DB、Redis、Celery 连接状态。
- **系统指标**: CPU、内存、Uptime 统计（仅管理员可见）。

---

## 5. 开发规范 (Development Guidelines)

### 代码风格
- **Python**: 遵循 PEP8，使用 Type Hints，Google-style Docstrings。
- **TypeScript**: 严格模式 (`strict: true`)，禁止 `any`，使用 Interface 定义数据结构。

### 目录结构规范
```
backend/
  ├── core/          # 核心抽象 (BaseCrawler)
  ├── crawlers/      # 具体爬虫实现
  ├── routers/       # API 路由
  ├── schemas/       # Pydantic 模型
  ├── crud/          # 数据库操作
  └── tasks/         # Celery/后台任务定义
frontend/
  ├── src/components # UI 组件
  ├── src/hooks      # 自定义 Hooks
  └── src/services   # API 客户端
```

### 提交流程
1. 分支命名: `feat/xxx`, `fix/xxx`
2. 提交信息: `[Phase X] feat: message`
3. 确保测试通过: `pytest tests/`

---

## 6. 部署指南 (Deployment)

### 生产环境配置
1. **数据库迁移**: 切换至 PostgreSQL。
   - 修改 `.env`: `DATABASE_URL=postgresql+asyncpg://...`
2. **任务队列**: 启用 Celery + Redis。
   - 设置 `USE_CELERY=true`
3. **反向代理**: 使用 Nginx 代理 API 与前端静态文件。

### Docker Compose 编排
- `docker-compose.yml`: 包含 Backend, Frontend (Nginx), Postgres, Redis, Celery Worker, Flower。
- **数据持久化**: 挂载 Volume 保证 DB 数据不丢失。

---

## 7. 项目路线图与阶段回顾 (Roadmap & Phases)

### Phase 1: 异步基础与 FastAPI (已完成)
- [x] 搭建 FastAPI 骨架
- [x] 实现 BaseCrawler 与异步封装
- [x] WebSocket 实时通信
- [x] JWT 认证体系

### Phase 2: 生产级增强 (已完成)
- [x] 集成 PostgreSQL
- [x] 引入 Celery + Redis 任务队列
- [x] Docker 容器化部署
- [x] 系统监控与健康检查

### Phase 3: 全栈交互 (已完成)
- [x] React 前端开发
- [x] 任务列表与详情页
- [x] 实时日志与进度条组件
- [x] 移动端响应式适配

### 未来规划
- **Phase 4**: 分布式爬虫集群与可视化报表
- **Phase 5**: AI 辅助解析与反爬策略集成

---

*文档最后更新时间: 2026-01-16*
