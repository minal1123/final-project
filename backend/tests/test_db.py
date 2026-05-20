# Unit tests for SQLite database operations
import os
import sys
import tempfile
import pytest

# Resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.database import db

@pytest.fixture(autouse=True)
def setup_test_db():
    """Fixture to create and clean up a temporary database file for tests."""
    fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Patch database path
    original_path = db.DB_PATH
    db.DB_PATH = temp_db_path
    
    db.init_db()
    
    yield
    
    # Restore and cleanup
    db.DB_PATH = original_path
    if os.path.exists(temp_db_path):
        try:
            os.remove(temp_db_path)
        except PermissionError:
            pass # Handle OS lock issues gracefully in cleanup

def test_save_and_retrieve_test_run():
    metrics = {
        "url": "http://127.0.0.1:5000/api/dummy/success",
        "method": "GET",
        "total_requests": 3,
        "success_count": 2,
        "failure_count": 1,
        "avg_response_time": 0.150,
        "min_response_time": 0.050,
        "max_response_time": 0.350,
        "requests_per_second": 20.0,
        "timestamp": "2026-05-20 12:00:00"
    }
    
    details = [
        {"request_index": 1, "status_code": 200, "response_time": 0.050, "success": True, "error_message": None},
        {"request_index": 2, "status_code": 200, "response_time": 0.050, "success": True, "error_message": None},
        {"request_index": 3, "status_code": 500, "response_time": 0.350, "success": False, "error_message": "HTTP Status 500"}
    ]
    
    # Save to SQLite
    run_id = db.save_test_run(metrics, details)
    assert run_id > 0
    
    # Query summary
    run = db.get_test_run(run_id)
    assert run is not None
    assert run["id"] == run_id
    assert run["url"] == metrics["url"]
    assert run["success_count"] == 2
    assert run["failure_count"] == 1
    
    # Query details
    db_details = db.get_test_run_details(run_id)
    assert len(db_details) == 3
    assert db_details[0]["request_index"] == 1
    assert db_details[0]["success"] == 1
    assert db_details[2]["success"] == 0
    assert db_details[2]["status_code"] == 500
    
    # Query all runs list
    all_runs = db.get_all_test_runs()
    assert len(all_runs) == 1
    assert all_runs[0]["id"] == run_id

def test_aggregate_stats():
    # Verify defaults on empty DB
    empty_stats = db.get_aggregate_stats()
    assert empty_stats["total_runs"] == 0
    assert empty_stats["success_rate"] == 100.0
    
    # Save a run
    metrics = {
        "url": "http://example.com/test",
        "method": "POST",
        "total_requests": 10,
        "success_count": 8,
        "failure_count": 2,
        "avg_response_time": 0.12,
        "min_response_time": 0.10,
        "max_response_time": 0.15,
        "requests_per_second": 83.3,
        "timestamp": "2026-05-20 12:05:00"
    }
    details = [{"request_index": i, "status_code": 200, "response_time": 0.12, "success": True, "error_message": None} for i in range(1, 11)]
    db.save_test_run(metrics, details)
    
    # Check stats
    stats = db.get_aggregate_stats()
    assert stats["total_runs"] == 1
    assert stats["total_requests"] == 10
    assert stats["success_rate"] == 80.0
    assert stats["overall_avg_response"] == 0.12
    assert stats["top_url"] == "http://example.com/test"

def test_delete_cascades():
    metrics = {
        "url": "http://127.0.0.1:5000/api/dummy/success",
        "method": "GET",
        "total_requests": 2,
        "success_count": 2,
        "failure_count": 0,
        "avg_response_time": 0.05,
        "min_response_time": 0.04,
        "max_response_time": 0.06,
        "requests_per_second": 40.0,
        "timestamp": "2026-05-20 12:10:00"
    }
    details = [
        {"request_index": 1, "status_code": 200, "response_time": 0.04, "success": True, "error_message": None},
        {"request_index": 2, "status_code": 200, "response_time": 0.06, "success": True, "error_message": None}
    ]
    
    run_id = db.save_test_run(metrics, details)
    
    # Delete
    deleted = db.delete_test_run(run_id)
    assert deleted is True
    
    # Verify cascaded details deletion
    assert db.get_test_run(run_id) is None
    assert len(db.get_test_run_details(run_id)) == 0
