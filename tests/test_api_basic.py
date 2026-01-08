"""
基础 API 测试
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["status"] == "running"


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_crawlers():
    """测试获取爬虫列表"""
    response = client.get("/api/crawlers")
    assert response.status_code == 200
    crawlers = response.json()
    
    # 应该至少有 3 个爬虫
    assert len(crawlers) >= 3
    
    # 检查爬虫名称
    crawler_names = [c["name"] for c in crawlers]
    assert "yahoo" in crawler_names
    assert "movies" in crawler_names
    assert "jobs" in crawler_names


def test_get_crawler_info():
    """测试获取特定爬虫信息"""
    response = client.get("/api/crawlers/yahoo")
    assert response.status_code == 200
    
    crawler = response.json()
    assert crawler["name"] == "yahoo"
    assert crawler["display_name"] == "Yahoo Finance"
    assert "symbol" in crawler["parameters"]


def test_get_nonexistent_crawler():
    """测试获取不存在的爬虫"""
    response = client.get("/api/crawlers/nonexistent")
    assert response.status_code == 404


def test_api_docs_available():
    """测试 API 文档可访问"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
