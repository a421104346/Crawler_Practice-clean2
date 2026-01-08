#!/bin/bash
# 启动 Celery Worker

set -e

echo "================================"
echo "启动 Celery Worker"
echo "================================"

# 设置环境变量
export USE_CELERY=true

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

cd backend

# 启动 Celery Worker
celery -A celery_app worker --loglevel=info --concurrency=4
