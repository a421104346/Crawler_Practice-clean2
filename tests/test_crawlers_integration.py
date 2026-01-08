"""
爬虫集成测试（需要实际网络连接）
可以使用 pytest -m "not slow" 跳过这些测试
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

client = TestClient(app)


@pytest.mark.slow
def test_run_yahoo_crawler():
    """测试运行 Yahoo 爬虫"""
    response = client.post(
        "/api/crawlers/yahoo/run",
        json={"symbol": "AAPL"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "task_id" in data
    
    # 等待任务完成
    task_id = data["task_id"]
    time.sleep(5)  # 等待5秒让任务完成
    
    # 检查任务状态
    task_response = client.get(f"/api/tasks/{task_id}")
    assert task_response.status_code == 200
    
    task = task_response.json()
    assert task["crawler_type"] == "yahoo"
    assert task["status"] in ["running", "completed"]


@pytest.mark.slow
def test_run_movies_crawler():
    """测试运行豆瓣电影爬虫"""
    response = client.post(
        "/api/crawlers/movies/run",
        json={"max_pages": 1}  # 只爬1页，快速测试
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data


@pytest.mark.slow
def test_run_jobs_crawler():
    """测试运行招聘爬虫"""
    response = client.post(
        "/api/crawlers/jobs/run",
        json={"search": "python"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data


def test_run_invalid_crawler():
    """测试运行不存在的爬虫"""
    response = client.post(
        "/api/crawlers/invalid/run",
        json={}
    )
    
    assert response.status_code == 404


def test_run_yahoo_without_symbol():
    """测试运行 Yahoo 爬虫但不提供 symbol 参数"""
    response = client.post(
        "/api/crawlers/yahoo/run",
        json={}
    )
    
    # 应该返回错误
    assert response.status_code in [400, 500]
