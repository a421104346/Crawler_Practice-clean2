# 🚀 爬虫管理平台 (Crawler Management Platform)

一个基于 **FastAPI + React + TypeScript** 的**生产级全栈异步爬虫管理系统**。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2.2-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 🎯 项目概述

**完整的三阶段开发，涵盖从原型到生产的全过程**

本项目是一个完整的全栈爬虫管理平台，支持：
- ✅ **多种爬虫集成** - Yahoo Finance、豆瓣电影、Remotive招聘
- ✅ **分布式任务队列** - Celery + Redis，支持大规模并发
- ✅ **实时进度推送** - WebSocket 实时通信
- ✅ **现代化前端** - React 18 + TypeScript + Tailwind CSS
- ✅ **JWT 认证系统** - 完整的用户认证和授权
- ✅ **生产级部署** - Docker + PostgreSQL + 监控
- ✅ **完整测试覆盖** - 单元测试 + 集成测试
- ✅ **详尽文档** - 24,000+ 字文档

### 📊 项目规模
- **代码量**: 6,000+ 行
- **文件数**: 65+ 个
- **API 端点**: 20+ 个
- **完成时间**: 3-4 天
- **生产就绪**: ✅

## 🏗️ 系统架构

### 完整架构图

```
┌──────────────────────────────────────────────┐
│           React Frontend (港口: 3000)         │
│  ┌────────────────────────────────────────┐  │
│  │  - 用户认证界面                        │  │
│  │  - 爬虫控制面板                        │  │
│  │  - 实时进度显示 (WebSocket)            │  │
│  │  - 任务历史 & 可视化                   │  │
│  └────────────────────────────────────────┘  │
└──────────────┬──────────────┬────────────────┘
               │ HTTP REST    │ WebSocket
               ▼              ▼
┌──────────────────────────────────────────────┐
│        FastAPI Backend (端口: 8000)          │
│  ┌────────────────────────────────────────┐  │
│  │  Routers → Services → CRUD → Models    │  │
│  │  - JWT 认证中间件                      │  │
│  │  - 请求日志中间件                      │  │
│  │  - 性能监控                            │  │
│  └────────────────────────────────────────┘  │
└──────────────┬──────────────┬────────────────┘
               ↓              ↓
     ┌─────────────┐    ┌──────────────┐
     │ PostgreSQL  │    │    Redis     │
     │  (数据库)   │    │ (消息队列)   │
     └─────────────┘    └──────┬───────┘
                               ↓
                    ┌──────────────────┐
                    │  Celery Workers  │
                    │  (异步任务处理)  │
                    └──────┬───────────┘
                           ↓
                    ┌──────────────────┐
                    │   爬虫核心库     │
                    │  BaseCrawler     │
                    │    ├─ Yahoo      │
                    │    ├─ Movies     │
                    │    └─ Jobs       │
                    └──────────────────┘
```

## 📁 项目结构

```
Crawler_Practice/
├── backend/                      # FastAPI 后端 (Phase 1+2)
│   ├── main.py                   # 主应用
│   ├── config.py                 # 配置管理
│   ├── database.py               # 数据库连接
│   ├── dependencies.py           # 依赖注入
│   ├── celery_app.py             # Celery 配置
│   ├── logger.py                 # 日志系统
│   ├── middleware.py             # 中间件
│   ├── monitoring.py             # 监控
│   │
│   ├── models/                   # SQLAlchemy 模型
│   │   └── task.py
│   │
│   ├── schemas/                  # Pydantic 模型
│   │   ├── auth.py
│   │   ├── crawler.py
│   │   └── task.py
│   │
│   ├── services/                 # 业务逻辑
│   │   └── crawler_service.py
│   │
│   ├── crud/                     # CRUD 操作
│   │   └── task.py
│   │
│   ├── routers/                  # API 路由
│   │   ├── auth.py               # 认证
│   │   ├── crawlers.py           # 爬虫管理
│   │   ├── tasks.py              # 任务管理
│   │   ├── websocket.py          # 实时通信
│   │   └── monitoring.py         # 监控
│   │
│   ├── tasks/                    # Celery 任务
│   │   └── crawler_tasks.py
│   │
│   ├── alembic/                  # 数据库迁移
│   ├── Dockerfile                # Docker 镜像
│   └── requirements.txt          # Python 依赖
│
├── frontend/                     # React 前端 (Phase 3) ✅
│   ├── src/
│   │   ├── components/           # 可复用组件
│   │   │   ├── TaskCard.tsx      # 任务卡片
│   │   │   └── CrawlerPanel.tsx  # 爬虫面板
│   │   │
│   │   ├── pages/                # 页面组件
│   │   │   ├── Login.tsx         # 登录页
│   │   │   ├── Register.tsx      # 注册页
│   │   │   ├── Dashboard.tsx     # 仪表板
│   │   │   └── History.tsx       # 历史页
│   │   │
│   │   ├── hooks/                # 自定义 Hooks
│   │   │   └── useWebSocket.ts   # WebSocket Hook
│   │   │
│   │   ├── services/             # API 服务
│   │   │   └── api.ts
│   │   │
│   │   ├── store/                # 状态管理
│   │   │   └── authStore.ts      # 认证状态
│   │   │
│   │   ├── types/                # 类型定义
│   │   │   └── index.ts
│   │   │
│   │   ├── App.tsx               # 根组件
│   │   └── main.tsx              # 入口文件
│   │
│   ├── package.json              # npm 依赖
│   ├── vite.config.ts            # Vite 配置
│   ├── tsconfig.json             # TS 配置
│   └── tailwind.config.js        # 样式配置
│
├── core/                         # 爬虫核心库
│   └── base_crawler.py           # 基础爬虫类
│
├── crawlers/                     # 具体爬虫实现
│   ├── yahoo.py                  # Yahoo Finance
│   ├── movies.py                 # 豆瓣电影
│   └── jobs.py                   # Remotive 招聘
│
├── tests/                        # 测试套件
│   ├── conftest.py
│   ├── test_api_basic.py
│   ├── test_auth.py
│   ├── test_tasks.py
│   └── test_crawlers_integration.py
│
├── scripts/                      # 部署脚本 (Phase 2)
│   ├── deploy.sh                 # 一键部署
│   ├── start-dev.sh              # 开发启动
│   ├── start-celery.sh           # Celery 启动
│   ├── backup-db.sh              # 数据库备份
│   └── restore-db.sh             # 数据库恢复
│
├── docker-compose.yml            # 生产环境配置
├── docker-compose.dev.yml        # 开发环境配置
├── .dockerignore
├── .gitignore
│
└── 文档/
    ├── README.md                 # 项目总览（本文档）
    ├── QUICKSTART.md             # 快速开始
    ├── DEPLOYMENT.md             # 部署指南
    ├── PHASE1_COMPLETE.md        # Phase 1 总结
    ├── PHASE2_COMPLETE.md        # Phase 2 总结
    ├── PHASE3_COMPLETE.md        # Phase 3 总结
    └── PROJECT_COMPLETE.md       # 项目完整总结
```
```

## 🚀 5分钟快速开始

### 方法 1: Docker 一键启动（推荐）⭐

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd Crawler_Practice

# 2. 配置环境
cp backend/.env.example .env.production
# 编辑 .env.production，修改 SECRET_KEY

# 3. 一键部署
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# 4. 访问应用
# 前端: http://localhost:3000
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
# Flower: http://localhost:5555
```

**默认账号：**
- 用户名: `admin`
- 密码: `admin123`

### 方法 2: 本地开发启动

```bash
# 终端 1: 后端
cd backend
pip install -r requirements.txt
python main.py

# 终端 2: 前端
cd frontend
npm install
npm run dev

# 访问 http://localhost:3000
```

### 快速测试

```bash
# 健康检查
curl http://localhost:8000/health

# 获取爬虫列表
curl http://localhost:8000/api/crawlers

# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 📖 API 使用指南

### 认证

#### 1. 注册用户

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### 2. 登录获取 Token

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**默认账号：**
- 用户名: `admin`
- 密码: `admin123`

或

- 用户名: `demo`
- 密码: `demo123`

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 3. 使用 Token 访问受保护的端点

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 爬虫管理

#### 1. 获取所有可用爬虫

```bash
curl -X GET "http://localhost:8000/api/crawlers"
```

响应：
```json
[
  {
    "name": "yahoo",
    "display_name": "Yahoo Finance",
    "description": "抓取 Yahoo Finance 股票数据",
    "parameters": ["symbol"],
    "optional_parameters": [],
    "status": "active"
  },
  {
    "name": "movies",
    "display_name": "豆瓣电影 Top250",
    "description": "抓取豆瓣电影 Top250 榜单",
    "parameters": [],
    "optional_parameters": ["max_pages"],
    "status": "active"
  },
  ...
]
```

#### 2. 运行 Yahoo Finance 爬虫

```bash
curl -X POST "http://localhost:8000/api/crawlers/yahoo/run" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL"
  }'
```

响应：
```json
{
  "status": "success",
  "task_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "message": "Task created successfully",
  "timestamp": "2026-01-08T10:00:00Z"
}
```

#### 3. 运行豆瓣电影爬虫

```bash
curl -X POST "http://localhost:8000/api/crawlers/movies/run" \
  -H "Content-Type: application/json" \
  -d '{
    "max_pages": 2
  }'
```

#### 4. 运行招聘爬虫

```bash
curl -X POST "http://localhost:8000/api/crawlers/jobs/run" \
  -H "Content-Type: application/json" \
  -d '{
    "search": "python",
    "category": "software-dev"
  }'
```

### 任务管理

#### 1. 获取任务状态

```bash
curl -X GET "http://localhost:8000/api/tasks/{task_id}"
```

响应：
```json
{
  "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "crawler_type": "yahoo",
  "status": "completed",
  "progress": 100,
  "params": {"symbol": "AAPL"},
  "result": {...},
  "error": null,
  "created_at": "2026-01-08T10:00:00Z",
  "completed_at": "2026-01-08T10:00:05Z",
  "duration": 5.2
}
```

#### 2. 获取任务列表（带分页和过滤）

```bash
# 获取所有任务
curl -X GET "http://localhost:8000/api/tasks?page=1&page_size=20"

# 过滤已完成的任务
curl -X GET "http://localhost:8000/api/tasks?status=completed"

# 过滤特定爬虫的任务
curl -X GET "http://localhost:8000/api/tasks?crawler_type=yahoo"
```

#### 3. 删除任务

```bash
curl -X DELETE "http://localhost:8000/api/tasks/{task_id}"
```

#### 4. 更新任务（例如取消任务）

```bash
curl -X PATCH "http://localhost:8000/api/tasks/{task_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "cancelled"
  }'
```

### WebSocket 实时进度

使用 WebSocket 监听任务进度：

```javascript
// 前端 JavaScript 示例
const taskId = "a1b2c3d4-5678-90ab-cdef-1234567890ab";
const ws = new WebSocket(`ws://localhost:8000/ws/tasks/${taskId}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Progress:", data.progress, "%");
  console.log("Status:", data.status);
  console.log("Message:", data.message);
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("WebSocket closed");
};
```

## 🧪 运行测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 运行特定测试

```bash
# 只运行基础 API 测试
pytest tests/test_api_basic.py -v

# 只运行认证测试
pytest tests/test_auth.py -v

# 跳过慢速测试（集成测试）
pytest -m "not slow" -v
```

### 查看测试覆盖率

```bash
pytest --cov=backend tests/ --cov-report=html
```

## 🏗️ 开发路线图

### Phase 1: FastAPI + 异步基础 ✅ (当前阶段)

- [x] FastAPI 项目结构
- [x] SQLAlchemy + AsyncSession
- [x] 爬虫服务整合
- [x] WebSocket 实时进度
- [x] JWT 认证
- [x] 单元测试

### Phase 2: 生产部署 (计划中)

- [ ] Celery + Redis 任务队列
- [ ] PostgreSQL 数据库迁移
- [ ] Docker + Docker Compose
- [ ] 日志系统优化
- [ ] 错误监控（Sentry）
- [ ] 部署到云端（Render/AWS）

### Phase 3: React 前端 (计划中)

- [ ] React + TypeScript 项目搭建
- [ ] 爬虫控制面板
- [ ] 实时进度显示
- [ ] 任务历史查看
- [ ] 数据可视化

## 📝 开发规范

### 代码风格

- Python: 遵循 PEP 8
- 类型提示: 所有函数必须有类型注解
- 文档字符串: 使用 Google 风格

### Git 提交规范

```
[Phase 1] feat: 添加 WebSocket 实时进度推送
[Phase 1] fix: 修复任务状态更新问题
[Phase 2] chore: 配置 Docker Compose
```

## 🐛 常见问题

### 1. 数据库文件权限问题

```bash
# Windows
icacls crawler_tasks.db /grant Everyone:F

# Linux/Mac
chmod 666 crawler_tasks.db
```

### 2. 端口被占用

```bash
# 查找占用 8000 端口的进程
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

### 3. 依赖安装失败

```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请联系：[your-email@example.com]

---

**Phase 1 完成！** 🎉

下一步：Phase 2 - 生产环境部署
