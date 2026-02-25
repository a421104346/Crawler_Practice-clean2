"""
Basic API tests
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["status"] == "running"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_crawlers():
    """Test get crawler list"""
    response = client.get("/api/crawlers")
    assert response.status_code == 200
    crawlers = response.json()
    
    # Should have at least 3 crawlers
    assert len(crawlers) >= 3
    
    # Check crawler names
    crawler_names = [c["name"] for c in crawlers]
    assert "yahoo" in crawler_names
    assert "movies" in crawler_names
    assert "jobs" in crawler_names


def test_get_crawler_info():
    """Test get specific crawler info"""
    response = client.get("/api/crawlers/yahoo")
    assert response.status_code == 200
    
    crawler = response.json()
    assert crawler["name"] == "yahoo"
    assert crawler["display_name"] == "Yahoo Finance"
    assert "symbol" in crawler["parameters"]


def test_get_nonexistent_crawler():
    """Test get nonexistent crawler"""
    response = client.get("/api/crawlers/nonexistent")
    assert response.status_code == 404


def test_api_docs_available():
    """Test API docs are accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
