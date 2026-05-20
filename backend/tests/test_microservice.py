# Unit tests for the Runner Microservice
import os
import sys
import json
import pytest
import unittest.mock as mock

# Resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from runner_service.app import app, active_runs

@pytest.fixture
def client():
    """Fixture to set up the microservice test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
    active_runs.clear()

def test_runner_health_check(client):
    """Verifies that the microservice health endpoint returns status and job count."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["service"] == "Load Testing Runner Microservice"
    assert data["status"] == "healthy"
    assert data["active_jobs_count"] == 0

def test_runner_start_invalid_params(client):
    """Verifies error responses when missing or invalid config parameters are sent."""
    # Missing URL
    response = client.post("/run/start", json={"requests": 5, "concurrency": 2})
    assert response.status_code == 400
    assert "URL parameter is required" in response.get_json()["error"]
    
    # Invalid numerical format
    response = client.post("/run/start", json={"url": "http://test.com", "concurrency": "not-a-number"})
    assert response.status_code == 400
    assert "Invalid numerical parameters" in response.get_json()["error"]

@mock.patch("runner_service.app.BackendLoadTester")
def test_runner_lifecycle_flow(mock_tester_cls, client):
    """Verifies start, status polling, and stopping on the microservice using mock engine."""
    # Setup mock instance
    mock_tester_instance = mock.Mock()
    mock_tester_cls.return_value = mock_tester_instance
    
    # Mock progress snapshot response
    mock_tester_instance.get_progress_snapshot.return_value = {
        "status": "running",
        "progress_percent": 20.0,
        "completed_count": 2,
        "total_requests": 10,
        "success_count": 2,
        "failure_count": 0,
        "avg_response_time": 0.05,
        "min_response_time": 0.05,
        "max_response_time": 0.05,
        "requests_per_second": 40.0,
        "elapsed_time": 0.05,
        "error_message": None,
        "timestamp": "2026-05-20 12:00:00",
        "details_count": 2,
        "details": []
    }
    
    # 1. Start a run
    payload = {
        "url": "http://test.com/endpoint",
        "method": "POST",
        "requests": 10,
        "concurrency": 2,
        "interval": 0.0,
        "timeout": 5.0
    }
    response = client.post("/run/start", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "task_id" in data
    assert data["status"] == "running"
    
    task_id = data["task_id"]
    
    # Verify mock engine calls
    mock_tester_cls.assert_called_once_with(
        url="http://test.com/endpoint",
        method="POST",
        headers={},
        body=None,
        total_requests=10,
        concurrency=2,
        interval=0.0,
        timeout=5.0
    )
    mock_tester_instance.start.assert_called_once()
    
    # 2. Poll Status
    status_response = client.get(f"/run/status/{task_id}")
    assert status_response.status_code == 200
    status_data = status_response.get_json()
    assert status_data["status"] == "running"
    assert status_data["progress_percent"] == 20.0
    mock_tester_instance.get_progress_snapshot.assert_called_once()
    
    # 3. Stop Run
    stop_response = client.post(f"/run/stop/{task_id}")
    assert stop_response.status_code == 200
    stop_data = stop_response.get_json()
    assert stop_data["status"] == "stopping_requested"
    mock_tester_instance.stop.assert_called_once()
