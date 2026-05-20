# Flask REST API endpoints and mock routes
from flask import Blueprint, request, jsonify
import uuid
import time
from backend.services.load_tester import BackendLoadTester
from backend.database import db

api_bp = Blueprint('api', __name__)

import requests

# In-memory dictionary to track active tests
# Format: { task_id: {"saved": bool, "url": str, "method": str} }
active_tests = {}

RUNNER_SERVICE_URL = "http://127.0.0.1:5001"

@api_bp.route('/test/start', methods=['POST'])
def start_test():
    """Starts a concurrent load test via the runner microservice."""
    data = request.get_json() or {}
    
    url = data.get('url')
    method = data.get('method', 'GET').upper()
    headers = data.get('headers', {})
    body = data.get('body')
    
    try:
        total_requests = int(data.get('requests', 100))
        concurrency = int(data.get('concurrency', 10))
        interval = float(data.get('interval', 0.0))
        timeout = float(data.get('timeout', 10.0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid numerical parameters."}), 400
        
    if not url:
        return jsonify({"error": "URL parameter is required."}), 400
        
    # Forward payload to the runner microservice
    payload = {
        "url": url,
        "method": method,
        "headers": headers,
        "body": body,
        "requests": total_requests,
        "concurrency": concurrency,
        "interval": interval,
        "timeout": timeout
    }
    
    try:
        r = requests.post(f"{RUNNER_SERVICE_URL}/run/start", json=payload, timeout=5)
        if r.status_code != 200:
            return jsonify({"error": f"Microservice returned error: {r.text}"}), r.status_code
        
        resp_data = r.json()
        task_id = resp_data["task_id"]
        
        active_tests[task_id] = {
            "saved": False,
            "url": url,
            "method": method
        }
        
        return jsonify({"task_id": task_id, "status": "running"})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to load testing runner microservice: {str(e)}"}), 502

@api_bp.route('/test/status/<task_id>', methods=['GET'])
def test_status(task_id):
    """Fetches progress metrics from microservice and saves to database if finished."""
    test_entry = active_tests.get(task_id)
    if not test_entry:
        return jsonify({"error": "Task not found."}), 404
        
    try:
        r = requests.get(f"{RUNNER_SERVICE_URL}/run/status/{task_id}", timeout=5)
        if r.status_code != 200:
            return jsonify({"error": f"Microservice status query failed: {r.text}"}), r.status_code
            
        snapshot = r.json()
        
        # Save completed tests to SQLite
        if snapshot["status"] in ["finished", "stopped"] and not test_entry["saved"]:
            try:
                metrics = {
                    "url": test_entry["url"],
                    "method": test_entry["method"],
                    "total_requests": snapshot["completed_count"],
                    "success_count": snapshot["success_count"],
                    "failure_count": snapshot["failure_count"],
                    "avg_response_time": snapshot["avg_response_time"],
                    "min_response_time": snapshot["min_response_time"],
                    "max_response_time": snapshot["max_response_time"],
                    "requests_per_second": snapshot["requests_per_second"],
                    "timestamp": snapshot["timestamp"]
                }
                
                # Save if we actually generated some details
                if len(snapshot["details"]) > 0:
                    run_id = db.save_test_run(metrics, snapshot["details"])
                    snapshot["db_run_id"] = run_id
                
                test_entry["saved"] = True
            except Exception as e:
                print(f"Error saving test run to DB: {e}")
                
        return jsonify(snapshot)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to runner microservice: {str(e)}"}), 502

@api_bp.route('/test/stop/<task_id>', methods=['POST'])
def stop_test(task_id):
    """Cancels a running test on the microservice."""
    test_entry = active_tests.get(task_id)
    if not test_entry:
        return jsonify({"error": "Task not found."}), 404
        
    try:
        r = requests.post(f"{RUNNER_SERVICE_URL}/run/stop/{task_id}", timeout=5)
        if r.status_code != 200:
            return jsonify({"error": f"Microservice stop query failed: {r.text}"}), r.status_code
        return jsonify(r.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to runner microservice: {str(e)}"}), 502

@api_bp.route('/history', methods=['GET'])
def get_history():
    """Returns all past test run summaries."""
    runs = db.get_all_test_runs()
    return jsonify(runs)

@api_bp.route('/history/<int:run_id>', methods=['GET'])
def get_history_detail(run_id):
    """Returns detailed statistics and individual request logs for a run."""
    run = db.get_test_run(run_id)
    if not run:
        return jsonify({"error": "Run not found."}), 404
        
    details = db.get_test_run_details(run_id)
    return jsonify({
        "metrics": run,
        "details": details
    })

@api_bp.route('/history/<int:run_id>', methods=['DELETE'])
def delete_history(run_id):
    """Deletes a past run record."""
    deleted = db.delete_test_run(run_id)
    if deleted:
        return jsonify({"success": True})
    return jsonify({"error": "Run not found or already deleted."}), 404

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Returns system-wide aggregated metrics."""
    stats = db.get_aggregate_stats()
    return jsonify(stats)


# ==========================================
# MOCK ENDPOINTS FOR LOCAL TESTING
# ==========================================

@api_bp.route('/dummy/success', methods=['GET', 'POST', 'PUT', 'DELETE'])
def dummy_success():
    """Mock API returning 200 OK instantly."""
    return jsonify({
        "status": "success",
        "message": "Mock API success response",
        "timestamp": time.time(),
        "method": request.method
    }), 200

@api_bp.route('/dummy/delay', methods=['GET', 'POST', 'PUT', 'DELETE'])
def dummy_delay():
    """Mock API simulating a delay (latency)."""
    # Delay in milliseconds
    delay_ms = request.args.get('ms', default=200, type=int)
    # Caps safety delay at 5 seconds
    delay_ms = min(max(0, delay_ms), 5000)
    
    time.sleep(delay_ms / 1000.0)
    
    return jsonify({
        "status": "delayed_success",
        "delay_applied_ms": delay_ms,
        "message": f"Responded after {delay_ms}ms sleep",
        "method": request.method
    }), 200

@api_bp.route('/dummy/error', methods=['GET', 'POST', 'PUT', 'DELETE'])
def dummy_error():
    """Mock API returning 500 Internal Server Error."""
    return jsonify({
        "status": "error",
        "message": "Simulated database connection failure in Mock API server."
    }), 500

@api_bp.route('/dummy/echo', methods=['POST', 'PUT'])
def dummy_echo():
    """Mock API echoing headers and body."""
    headers = dict(request.headers)
    body = request.get_json(silent=True) or request.form.to_dict() or request.data.decode('utf-8')
    
    return jsonify({
        "status": "echo",
        "received_headers": headers,
        "received_body": body
    }), 200
