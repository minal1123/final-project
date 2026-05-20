# Unit tests for Flask API routes and load tester bindings
import os
import sys
import json
import pytest
import tempfile

# Resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app import create_app
from backend.database import db
from backend.services.load_tester import BackendLoadTester

@pytest.fixture
def client():
    """Fixture to set up a clean Flask test client with a temporary database."""
    fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Patch database path
    original_path = db.DB_PATH
    db.DB_PATH = temp_db_path
    
    app = create_app()
    app.config["TESTING"] = True
    
    with app.test_client() as client:
        yield client
        
    db.DB_PATH = original_path
    if os.path.exists(temp_db_path):
        try:
            os.remove(temp_db_path)
        except PermissionError:
            pass

def test_health_check(client):
    """Verifies that the index endpoint returns service health metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "API Load Testing" in data["service"]

def test_dummy_success_route(client):
    """Verifies standard mock success API return format."""
    response = client.get("/api/dummy/success")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "Mock API success" in data["message"]

def test_dummy_delay_route(client):
    """Verifies mock delay API handles ms query parameters."""
    response = client.get("/api/dummy/delay?ms=50")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "delayed_success"
    assert data["delay_applied_ms"] == 50

def test_dummy_error_route(client):
    """Verifies mock error API correctly returns 500 error."""
    response = client.get("/api/dummy/error")
    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "error"

def test_dummy_echo_route(client):
    """Verifies mock echo API returns payload and request headers."""
    payload = {"foo": "bar", "num": 123}
    response = client.post("/api/dummy/echo", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "echo"
    assert data["received_body"]["foo"] == "bar"

def test_empty_database_routes(client):
    """Verifies database endpoints respond safely when database is empty."""
    # History list check
    response = client.get("/api/history")
    assert response.status_code == 200
    assert len(response.get_json()) == 0
    
    # Stats check
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total_runs"] == 0
    assert data["success_rate"] == 100.0
    
    # Non-existent run details check
    response = client.get("/api/history/999")
    assert response.status_code == 404

def test_tester_thread_execution():
    """Verifies that the concurrent thread-safe tester completes and computes correct stats."""
    # Test against mock-like local payload using low count
    tester = BackendLoadTester(
        url="https://httpbin.org/get", # Or any standard domain
        method="GET",
        total_requests=2,
        concurrency=2,
        timeout=3.0
    )
    
    # We can fake request sending or run a quick real local test if offline.
    # To make tests extremely reliable and offline-friendly, let's mock the requests.request call!
    import unittest.mock as mock
    
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.elapsed.total_seconds.return_value = 0.05
    
    with mock.patch("requests.request", return_value=mock_response):
        tester.start()
        # Wait for finish
        for _ in range(20):
            time_snapshot = tester.get_progress_snapshot()
            if time_snapshot["status"] in ["finished", "error", "stopped"]:
                break
            import time
            time.sleep(0.1)
            
        snapshot = tester.get_progress_snapshot()
        assert snapshot["status"] == "finished"
        assert snapshot["completed_count"] == 2
        assert snapshot["success_count"] == 2
        assert snapshot["failure_count"] == 0
        assert len(snapshot["details"]) == 2
        assert snapshot["details"][0]["success"] == 1
