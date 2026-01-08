"""
认证系统测试
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_register_new_user():
    """测试注册新用户"""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_register_duplicate_username():
    """测试注册重复用户名"""
    # 第一次注册
    client.post(
        "/api/auth/register",
        json={
            "username": "duplicate",
            "email": "dup1@example.com",
            "password": "pass123"
        }
    )
    
    # 第二次注册相同用户名
    response = client.post(
        "/api/auth/register",
        json={
            "username": "duplicate",
            "email": "dup2@example.com",
            "password": "pass456"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success():
    """测试成功登录"""
    # 默认用户：admin / admin123
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


def test_login_invalid_password():
    """测试错误密码登录"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]


def test_login_nonexistent_user():
    """测试不存在的用户登录"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "nonexistent",
            "password": "anypassword"
        }
    )
    
    assert response.status_code == 401


def test_get_current_user():
    """测试获取当前用户信息"""
    # 先登录
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # 获取用户信息
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"


def test_get_current_user_without_token():
    """测试未认证访问受保护的端点"""
    response = client.get("/api/auth/me")
    assert response.status_code == 403  # Forbidden


def test_get_current_user_with_invalid_token():
    """测试使用无效 token 访问"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_logout():
    """测试登出"""
    # 先登录
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # 登出
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert "Successfully logged out" in response.json()["message"]
