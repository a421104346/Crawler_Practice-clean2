#!/bin/bash
# 生产环境部署脚本

set -e  # 遇到错误立即退出

echo "================================"
echo "Crawler API 生产环境部署"
echo "================================"

# 颜色输出
GREEN='\033[0.32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    exit 1
fi

# 检查 .env.production 是否存在
if [ ! -f ".env.production" ]; then
    echo -e "${RED}错误: .env.production 文件不存在${NC}"
    echo "请从 .env.example 复制并配置生产环境变量"
    exit 1
fi

# 停止现有容器
echo "停止现有容器..."
docker-compose down

# 构建新镜像
echo "构建 Docker 镜像..."
docker-compose build --no-cache

# 运行数据库迁移
echo "运行数据库迁移..."
docker-compose run --rm backend alembic upgrade head

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务就绪
echo "等待服务启动..."
sleep 10

# 健康检查
echo "执行健康检查..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 部署成功！${NC}"
    echo ""
    echo "服务访问地址："
    echo "  - API: http://localhost:8000"
    echo "  - API 文档: http://localhost:8000/docs"
    echo "  - Flower (Celery 监控): http://localhost:5555"
    echo ""
    echo "查看日志："
    echo "  docker-compose logs -f"
else
    echo -e "${RED}✗ 健康检查失败${NC}"
    echo "查看日志："
    echo "  docker-compose logs"
    exit 1
fi
