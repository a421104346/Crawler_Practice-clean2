"""
Crawler integration tests (requires actual network connection)
Use pytest -m "not slow" to skip these tests
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

client = TestClient(app)


@pytest.mark.slow
def test_run_yahoo_crawler():
    """Test running Yahoo crawler"""
    response = client.post(
        "/api/crawlers/yahoo/run",
        json={"symbol": "AAPL"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "task_id" in data
    
    # Wait for task to complete
    task_id = data["task_id"]
    time.sleep(5)  # Wait 5 seconds for task to complete
    
    # Check task status
    task_response = client.get(f"/api/tasks/{task_id}")
    assert task_response.status_code == 200
    
    task = task_response.json()
    assert task["crawler_type"] == "yahoo"
    assert task["status"] in ["running", "completed"]


@pytest.mark.slow
def test_run_movies_crawler():
    """Test running movies crawler"""
    response = client.post(
        "/api/crawlers/movies/run",
        json={"max_pages": 1}  # Only crawl 1 page for quick test
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data


@pytest.mark.slow
def test_run_jobs_crawler():
    """Test running jobs crawler"""
    response = client.post(
        "/api/crawlers/jobs/run",
        json={"search": "python"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data


def test_run_invalid_crawler():
    """Test running nonexistent crawler"""
    response = client.post(
        "/api/crawlers/invalid/run",
        json={}
    )
    
    assert response.status_code == 404


def test_run_yahoo_without_symbol():
    """Test running Yahoo crawler without symbol parameter"""
    response = client.post(
        "/api/crawlers/yahoo/run",
        json={}
    )
    
    # Should return error
    assert response.status_code in [400, 500]
