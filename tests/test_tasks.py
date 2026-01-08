"""
任务管理测试
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_tasks_list():
    """测试获取任务列表"""
    response = client.get("/api/tasks")
    assert response.status_code == 200
    
    data = response.json()
    assert "total" in data
    assert "tasks" in data
    assert "page" in data
    assert isinstance(data["tasks"], list)


def test_get_tasks_with_pagination():
    """测试任务列表分页"""
    response = client.get("/api/tasks?page=1&page_size=10")
    assert response.status_code == 200
    
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_get_tasks_with_filter():
    """测试任务列表过滤"""
    # 按状态过滤
    response = client.get("/api/tasks?status=completed")
    assert response.status_code == 200
    
    # 按爬虫类型过滤
    response = client.get("/api/tasks?crawler_type=yahoo")
    assert response.status_code == 200


def test_get_nonexistent_task():
    """测试获取不存在的任务"""
    response = client.get("/api/tasks/nonexistent-task-id")
    assert response.status_code == 404


def test_create_and_get_task():
    """测试创建任务并获取"""
    # 创建任务
    create_response = client.post(
        "/api/crawlers/yahoo/run",
        json={"symbol": "MSFT"}
    )
    
    assert create_response.status_code == 200
    task_id = create_response.json()["task_id"]
    
    # 获取任务
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 200
    
    task = get_response.json()
    assert task["id"] == task_id
    assert task["crawler_type"] == "yahoo"
    assert task["status"] in ["pending", "running"]


def test_delete_task():
    """测试删除任务"""
    # 创建任务
    create_response = client.post(
        "/api/crawlers/movies/run",
        json={"max_pages": 1}
    )
    task_id = create_response.json()["task_id"]
    
    # 删除任务
    delete_response = client.delete(f"/api/tasks/{task_id}")
    assert delete_response.status_code == 200
    
    # 验证任务已删除
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404


def test_update_task():
    """测试更新任务状态"""
    # 创建任务
    create_response = client.post(
        "/api/crawlers/yahoo/run",
        json={"symbol": "GOOGL"}
    )
    task_id = create_response.json()["task_id"]
    
    # 更新任务（例如取消任务）
    update_response = client.patch(
        f"/api/tasks/{task_id}",
        json={"status": "cancelled"}
    )
    
    assert update_response.status_code == 200
    
    task = update_response.json()
    assert task["status"] == "cancelled"
