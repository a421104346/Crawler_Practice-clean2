"""
Pytest configuration: shared fixtures and test config
"""
import os
import sys
from pathlib import Path

# 1. Set environment variables before importing any backend modules
# This ensures settings and database use test config
os.environ["DEBUG"] = "False"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_crawler_tasks.db"
os.environ["USE_CELERY"] = "False"  # Disable Celery, force BackgroundTasks

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import patch
from sqlalchemy import text

# Now import backend modules
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Explicitly import all models to ensure they are registered in Base.metadata
# Note: must set env vars before importing these, as database.py initializes engine on import
from backend.models.task import TaskModel
from backend.main import app
from backend.database import Base, get_db
from backend.config import settings

# Test database URL
TEST_DATABASE_URL = settings.DATABASE_URL

@pytest.fixture(scope="session", autouse=True)
def cleanup_db():
    """Clean up test database file"""
    db_file = "./test_crawler_tasks.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    yield
    if os.path.exists(db_file):
        os.remove(db_file)

@pytest.fixture(scope="function")
async def test_db():
    """Create test database"""
    # At this point settings.DATABASE_URL should point to test DB
    # backend.database.engine should also point to test DB
    from backend.database import engine
    
    # Create all tables
    async with engine.begin() as conn:
        # Force use of TaskModel.metadata
        await conn.run_sync(TaskModel.metadata.create_all)
        # Double insurance
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
    
    # Create session
    # Directly use AsyncSessionLocal from backend.database
    # Since it's already connected to the test engine
    from backend.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        yield session
    
    # Clean up tables (optional)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client"""
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Get authenticated headers (token after login)"""
    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # If login fails, register first
        client.post(
            "/api/auth/register",
            json={
                "username": "admin",
                "email": "admin@test.com",
                "password": "admin123"
            }
        )
        
        # Login again
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
