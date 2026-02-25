"""
Authentication system tests
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_register_new_user():
    """Test register new user"""
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
    """Test register duplicate username"""
    # First registration
    client.post(
        "/api/auth/register",
        json={
            "username": "duplicate",
            "email": "dup1@example.com",
            "password": "pass123"
        }
    )
    
    # Second registration with same username
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
    """Test successful login"""
    # Default user: admin / admin123
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
    """Test login with invalid password"""
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
    """Test login with nonexistent user"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "nonexistent",
            "password": "anypassword"
        }
    )
    
    assert response.status_code == 401


def test_get_current_user():
    """Test get current user info"""
    # Login first
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Get user info
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"


def test_get_current_user_without_token():
    """Test unauthenticated access to protected endpoint"""
    response = client.get("/api/auth/me")
    assert response.status_code == 403  # Forbidden


def test_get_current_user_with_invalid_token():
    """Test access with invalid token"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_logout():
    """Test logout"""
    # Login first
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Logout
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert "Successfully logged out" in response.json()["message"]
