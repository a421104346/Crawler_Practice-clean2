"""
Task management tests
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_tasks_list():
    """Test get task list"""
    response = client.get("/api/tasks")
    assert response.status_code == 200
    
    data = response.json()
    assert "total" in data
    assert "tasks" in data
    assert "page" in data
    assert isinstance(data["tasks"], list)


def test_get_tasks_with_pagination():
    """Test task list pagination"""
    response = client.get("/api/tasks?page=1&page_size=10")
    assert response.status_code == 200
    
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_get_tasks_with_filter():
    """Test task list filtering"""
    # Filter by status
    response = client.get("/api/tasks?status=completed")
    assert response.status_code == 200
    
    # Filter by crawler type
    response = client.get("/api/tasks?crawler_type=yahoo")
    assert response.status_code == 200


def test_get_nonexistent_task():
    """Test get nonexistent task"""
    response = client.get("/api/tasks/nonexistent-task-id")
    assert response.status_code == 404


def test_create_and_get_task():
    """Test create and get task"""
    # Create task
    create_response = client.post(
        "/api/crawlers/yahoo/run",
        json={"symbol": "MSFT"}
    )
    
    assert create_response.status_code == 200
    task_id = create_response.json()["task_id"]
    
    # Get task
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 200
    
    task = get_response.json()
    assert task["id"] == task_id
    assert task["crawler_type"] == "yahoo"
    assert task["status"] in ["pending", "running"]


def test_delete_task():
    """Test delete task"""
    # Create task
    create_response = client.post(
        "/api/crawlers/movies/run",
        json={"max_pages": 1}
    )
    task_id = create_response.json()["task_id"]
    
    # Delete task
    delete_response = client.delete(f"/api/tasks/{task_id}")
    assert delete_response.status_code == 200
    
    # Verify task is deleted
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404


def test_update_task():
    """Test update task status"""
    # Create task
    create_response = client.post(
        "/api/crawlers/yahoo/run",
        json={"symbol": "GOOGL"}
    )
    task_id = create_response.json()["task_id"]
    
    # Update task (e.g. cancel task)
    update_response = client.patch(
        f"/api/tasks/{task_id}",
        json={"status": "cancelled"}
    )
    
    assert update_response.status_code == 200
    
    task = update_response.json()
    assert task["status"] == "cancelled"
