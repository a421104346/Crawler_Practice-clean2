#!/bin/bash
# 开发环境启动脚本

set -e

echo "================================"
echo "启动开发环境"
echo "================================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
cd backend
pip install -r requirements.txt

# 初始化数据库
echo "初始化数据库..."
python -c "import asyncio; from database import init_db; asyncio.run(init_db())"

# 启动服务
echo "启动 FastAPI 服务..."
echo ""
echo "访问地址："
echo "  - API: http://localhost:8000"
echo "  - 文档: http://localhost:8000/docs"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
