# 部署指南

完整的生产环境部署文档。

## 📋 前置要求

### 系统要求
- Linux 服务器（Ubuntu 20.04+ 或 CentOS 8+ 推荐）
- 至少 2GB RAM
- 20GB 可用磁盘空间
- Docker 20.10+
- Docker Compose 2.0+

### 安装 Docker

```bash
# Ubuntu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 🚀 快速部署

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd Crawler_Practice
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp backend/.env.example .env.production

# 编辑生产环境配置
nano .env.production
```

**重要配置项：**

```bash
# 必须修改！
SECRET_KEY="使用 openssl rand -hex 32 生成"

# PostgreSQL 数据库
DATABASE_URL="postgresql+asyncpg://crawler_user:STRONG_PASSWORD@postgres:5432/crawler_db"

# Redis
REDIS_URL="redis://redis:6379/0"

# CORS（你的前端域名）
CORS_ORIGINS=["https://yourdomain.com"]
```

### 3. 一键部署

```bash
# 给脚本执行权限
chmod +x scripts/*.sh

# 执行部署
./scripts/deploy.sh
```

部署脚本会自动：
1. 构建 Docker 镜像
2. 运行数据库迁移
3. 启动所有服务
4. 执行健康检查

### 4. 验证部署

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试 API
curl http://localhost:8000/health
```

## 📦 服务说明

部署后会启动以下服务：

| 服务 | 端口 | 说明 |
|------|------|------|
| backend | 8000 | FastAPI 主应用 |
| postgres | 5432 | PostgreSQL 数据库 |
| redis | 6379 | Redis 缓存/消息队列 |
| celery_worker | - | Celery 异步任务处理器 |
| celery_beat | - | Celery 定时任务调度器 |
| flower | 5555 | Celery 监控面板 |

## 🔧 常用命令

### 启动/停止服务

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启特定服务
docker-compose restart backend

# 查看日志
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### 数据库管理

```bash
# 运行数据库迁移
docker-compose run --rm backend alembic upgrade head

# 创建新迁移
docker-compose run --rm backend alembic revision --autogenerate -m "描述"

# 备份数据库
./scripts/backup-db.sh

# 恢复数据库
./scripts/restore-db.sh backups/crawler_db_20260108_120000.sql.gz
```

### 查看监控

```bash
# 打开 Flower 监控面板
open http://localhost:5555

# 查看系统指标（需要 admin 权限）
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/monitoring/metrics

# 健康检查
curl http://localhost:8000/api/monitoring/health/detailed
```

## 🔐 安全配置

### 1. 修改默认密码

```bash
# 生成强密码
openssl rand -base64 32

# 更新 .env.production
SECRET_KEY="新生成的密钥"
```

### 2. 配置防火墙

```bash
# 只开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. 使用 HTTPS

推荐使用 Nginx + Let's Encrypt：

```bash
# 安装 Nginx
sudo apt install nginx

# 配置反向代理
sudo nano /etc/nginx/sites-available/crawler-api

# 获取 SSL 证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

Nginx 配置示例：

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket 支持
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📊 性能优化

### 1. 调整 Worker 数量

编辑 `docker-compose.yml`：

```yaml
backend:
  environment:
    - WORKER_COUNT=8  # 根据 CPU 核心数调整

celery_worker:
  command: celery -A backend.celery_app worker --loglevel=info --concurrency=8
```

### 2. 数据库连接池

编辑 `backend/database.py`：

```python
engine_kwargs = {
    "pool_size": 20,      # 增加连接池大小
    "max_overflow": 40,
}
```

### 3. Redis 持久化

编辑 `docker-compose.yml`：

```yaml
redis:
  command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
```

## 🔍 故障排查

### 1. 容器无法启动

```bash
# 查看详细日志
docker-compose logs backend

# 检查容器状态
docker ps -a

# 重建容器
docker-compose up -d --force-recreate
```

### 2. 数据库连接失败

```bash
# 检查 PostgreSQL 状态
docker-compose exec postgres pg_isready

# 测试连接
docker-compose exec postgres psql -U crawler_user -d crawler_db -c "SELECT 1"
```

### 3. Celery Worker 不工作

```bash
# 查看 Worker 日志
docker-compose logs celery_worker

# 检查 Redis 连接
docker-compose exec redis redis-cli ping

# 重启 Worker
docker-compose restart celery_worker
```

### 4. 内存不足

```bash
# 查看内存使用
docker stats

# 限制容器内存
docker-compose.yml:
  services:
    backend:
      mem_limit: 1g
```

## 📈 扩展部署

### 多台服务器部署

1. **数据库服务器**：单独部署 PostgreSQL
2. **应用服务器**：部署多个 backend 实例（负载均衡）
3. **队列服务器**：部署 Redis + Celery Workers

### 使用云服务

#### AWS 部署示例

```bash
# 使用 ECS/EKS
aws ecs create-cluster --cluster-name crawler-cluster

# 使用 RDS
aws rds create-db-instance \
  --db-instance-identifier crawler-db \
  --engine postgres \
  --master-username admin \
  --master-user-password <password>

# 使用 ElastiCache (Redis)
aws elasticache create-cache-cluster \
  --cache-cluster-id crawler-redis \
  --engine redis
```

## 🔄 更新部署

### 零停机更新

```bash
# 拉取最新代码
git pull

# 构建新镜像
docker-compose build

# 滚动更新
docker-compose up -d --no-deps --build backend

# 运行迁移（如果有）
docker-compose run --rm backend alembic upgrade head
```

## 📝 监控和日志

### 集中日志管理

推荐使用 ELK Stack 或 Loki：

```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 性能监控

推荐使用：
- **Prometheus + Grafana**：指标收集和可视化
- **Sentry**：错误追踪
- **New Relic / DataDog**：APM 监控

## 📞 技术支持

如遇到问题：

1. 查看[故障排查](#故障排查)
2. 检查 GitHub Issues
3. 查看详细日志：`docker-compose logs -f`

---

**部署完成！** 🎉

访问你的 API：http://yourdomain.com
