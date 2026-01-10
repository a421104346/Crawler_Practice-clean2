"""
Pytest 配置文件：共享的 fixtures 和测试配置
"""
import os
import sys
from pathlib import Path

# 1. 在导入任何 backend 模块之前设置环境变量
# 这样能确保 settings 和 database 使用测试配置
os.environ["DEBUG"] = "False"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_crawler_tasks.db"
os.environ["USE_CELERY"] = "False"  # 禁用 Celery，强制使用 BackgroundTasks

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import patch
from sqlalchemy import text

# 现在才导入 backend 模块
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# 显式导入所有模型，确保它们在 Base.metadata 中注册
# 注意：必须先设置环境变量，再导入这些，因为 database.py 会在导入时初始化 engine
from backend.models.task import TaskModel
from backend.main import app
from backend.database import Base, get_db
from backend.config import settings

# 测试数据库 URL
TEST_DATABASE_URL = settings.DATABASE_URL

@pytest.fixture(scope="session", autouse=True)
def cleanup_db():
    """清理测试数据库文件"""
    db_file = "./test_crawler_tasks.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    yield
    if os.path.exists(db_file):
        os.remove(db_file)

@pytest.fixture(scope="function")
async def test_db():
    """创建测试数据库"""
    # 此时 settings.DATABASE_URL 应该已经是测试库了
    # backend.database.engine 也应该指向测试库
    from backend.database import engine
    
    # 创建所有表
    async with engine.begin() as conn:
        # 强制使用 TaskModel.metadata
        await conn.run_sync(TaskModel.metadata.create_all)
        # 双重保险
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tasks (
                id VARCHAR(36) PRIMARY KEY, 
                crawler_type VARCHAR(50) NOT NULL, 
                status VARCHAR(20) NOT NULL DEFAULT 'pending', 
                progress INTEGER DEFAULT 0, 
                params TEXT, 
                result TEXT, 
                error TEXT, 
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
                started_at DATETIME, 
                completed_at DATETIME, 
                duration FLOAT, 
                user_id VARCHAR(50)
            )
        """))
    
    # 创建会话
    # 直接使用 backend.database 里的 AsyncSessionLocal
    # 因为它已经连接到测试 engine 了
    from backend.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        yield session
    
    # 清理表（可选）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(test_db):
    """创建测试客户端"""
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """获取认证 headers（登录后的 token）"""
    # 登录获取 token
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # 如果登录失败，先注册
        client.post(
            "/api/auth/register",
            json={
                "username": "admin",
                "email": "admin@test.com",
                "password": "admin123"
            }
        )
        
        # 再次登录
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
