"""
Pytest 配置文件：共享的 fixtures 和测试配置
"""
import pytest
import sys
import os
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.main import app
from backend.database import Base, get_db
from backend.config import settings


# 测试数据库 URL（使用内存数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_db():
    """创建测试数据库"""
    # 创建异步引擎
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话工厂
    TestSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # 返回会话
    async with TestSessionLocal() as session:
        yield session
    
    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
def client(test_db):
    """创建测试客户端"""
    
    async def override_get_db():
        yield test_db
    
    # 替换数据库依赖
    app.dependency_overrides[get_db] = override_get_db
    
    # 创建测试客户端
    with TestClient(app) as c:
        yield c
    
    # 清理
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
