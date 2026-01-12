# Phase 2 快速开始指南

## 🚀 5分钟快速部署

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 快速启动

```bash
# 1. 配置环境变量（首次部署）
cp backend/.env.example .env.production
# 编辑 .env.production，至少修改 SECRET_KEY

# 2. 一键部署
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# 3. 访问服务
# API: http://localhost:8000
# 文档: http://localhost:8000/docs
# Flower: http://localhost:5555
```

就这么简单！🎉

---

## 📋 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| FastAPI | 8000 | 主 API |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存/队列 |
| Flower | 5555 | Celery 监控 |

---

## 🔧 常用命令

### Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart backend

# 查看状态
docker-compose ps
```

### 数据库管理

```bash
# 运行迁移
docker-compose run --rm backend alembic upgrade head

# 备份数据库
./scripts/backup-db.sh

# 恢复数据库
./scripts/restore-db.sh backups/xxx.sql.gz
```

### Celery 管理

```bash
# 查看 Worker 日志
docker-compose logs -f celery_worker

# 重启 Worker
docker-compose restart celery_worker

# 打开 Flower 监控
open http://localhost:5555
```

---

## 🎯 测试部署

### 1. 健康检查

```bash
# 基础检查
curl http://localhost:8000/health

# 详细检查（包括所有服务）
curl http://localhost:8000/api/monitoring/health/detailed | jq
```

### 2. 运行爬虫任务

```bash
# 登录获取 token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 运行 Yahoo 爬虫
curl -X POST http://localhost:8000/api/crawlers/yahoo/run \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL"}' \
  | jq
```

### 3. 查看任务

```bash
# 获取任务列表
curl http://localhost:8000/api/tasks | jq

# 查看特定任务
curl http://localhost:8000/api/tasks/{task_id} | jq
```

---

## 🔍 监控

### Flower 面板

访问 http://localhost:5555

- 查看活跃 Worker
- 监控任务执行
- 查看任务历史

### 系统指标

```bash
# 获取系统指标（需要 admin 权限）
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/monitoring/metrics | jq

# 任务统计
curl http://localhost:8000/api/monitoring/stats | jq
```

---

## 🐛 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker-compose logs backend

# 重建容器
docker-compose up -d --force-recreate
```

### 数据库连接失败

```bash
# 检查 PostgreSQL
docker-compose exec postgres pg_isready

# 测试连接
docker-compose exec postgres psql -U crawler_user -d crawler_db -c "SELECT 1"
```

### Celery Worker 不工作

```bash
# 查看 Worker 日志
docker-compose logs celery_worker

# 检查 Redis
docker-compose exec redis redis-cli ping

# 重启所有服务
docker-compose restart
```

---

## 📖 完整文档

详细内容请参考：

- `DEPLOYMENT.md` - 完整部署指南
- `PHASE2_COMPLETE.md` - Phase 2 功能总结
- `README.md` - 项目总览

---

## 💡 快速提示

### 开发模式

使用开发配置文件（热重载）：

```bash
docker-compose -f docker-compose.dev.yml up
```

### 仅 PostgreSQL + Redis

如果只需要数据库和缓存：

```bash
docker-compose up -d postgres redis
```

然后本地运行 FastAPI：

```bash
cd backend
python main.py
```

### 查看实时日志

```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

---

**快速开始完成！享受生产级应用！** 🎊
