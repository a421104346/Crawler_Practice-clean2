# 爬虫管理平台 (Crawler Management Platform)

一个基于 **FastAPI + React + TypeScript** 的生产级异步爬虫管理系统。

## 🎯 项目概述

本项目是一个完整的爬虫管理平台，支持：
- ✅ 多种爬虫集成（Yahoo Finance、豆瓣电影、Remotive招聘等）
- ✅ 异步任务处理（基于 FastAPI BackgroundTasks）
- ✅ 实时进度推送（WebSocket）
- ✅ JWT 认证系统
- ✅ RESTful API 设计
- ✅ 数据库持久化（SQLite -> PostgreSQL）
- ✅ 完整的测试覆盖

## 📁 项目结构

```
Crawler_Practice/
├── backend/                      # FastAPI 后端
│   ├── config.py                 # 配置管理
│   ├── database.py               # 数据库连接
│   ├── dependencies.py           # 依赖注入
│   ├── main.py                   # 主应用
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
│   ├── crud/                     # 数据库操作
│   │   └── task.py
│   │
│   └── routers/                  # API 路由
│       ├── auth.py               # 认证
│       ├── crawlers.py           # 爬虫管理
│       ├── tasks.py              # 任务管理
│       └── websocket.py          # 实时通信
│
├── core/                         # 爬虫核心库
│   ├── base_crawler.py           # 基础爬虫类
│   └── utils.py
│
├── crawlers/                     # 具体爬虫实现
│   ├── yahoo.py                  # Yahoo Finance
│   ├── movies.py                 # 豆瓣电影
│   └── jobs.py                   # Remotive 招聘
│
├── tests/                        # 测试
│   ├── conftest.py
│   ├── test_api_basic.py
│   ├── test_auth.py
│   ├── test_crawlers_integration.py
│   └── test_tasks.py
│
└── frontend/                     # React 前端 (Phase 3)
    └── (待开发)
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- pip / conda

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 到 `.env` 并修改配置：

```bash
cp .env.example .env
```

主要配置项：
- `DATABASE_URL`: 数据库连接字符串
- `SECRET_KEY`: JWT 密钥（生产环境必须修改！）
- `CORS_ORIGINS`: 允许的跨域来源

### 4. 运行应用

```bash
# 开发模式（带热重载）
cd backend
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

应用将在 http://localhost:8000 启动

### 5. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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
