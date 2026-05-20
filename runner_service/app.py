# Runner Microservice for API Load Testing Dashboard
import os
import sys
import uuid
from flask import Flask, request, jsonify

# Ensure project root is in path to import backend services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.load_tester import BackendLoadTester

app = Flask(__name__)

# Track active tests executed by this worker node
active_runs = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "service": "Load Testing Runner Microservice",
        "status": "healthy",
        "active_jobs_count": len([r for r in active_runs.values() if r.status == "running"])
    })

@app.route('/run/start', methods=['POST'])
def start_run():
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
        
    # Instantiate and start the load tester engine
    tester = BackendLoadTester(
        url=url,
        method=method,
        headers=headers,
        body=body,
        total_requests=total_requests,
        concurrency=concurrency,
        interval=interval,
        timeout=timeout
    )
    
    task_id = str(uuid.uuid4())
    active_runs[task_id] = tester
    tester.start()
    
    return jsonify({
        "task_id": task_id,
        "status": "running"
    })

@app.route('/run/status/<task_id>', methods=['GET'])
def run_status(task_id):
    tester = active_runs.get(task_id)
    if not tester:
        return jsonify({"error": "Job not found on this worker."}), 404
        
    snapshot = tester.get_progress_snapshot()
    return jsonify(snapshot)

@app.route('/run/stop/<task_id>', methods=['POST'])
def stop_run(task_id):
    tester = active_runs.get(task_id)
    if not tester:
        return jsonify({"error": "Job not found on this worker."}), 404
        
    tester.stop()
    return jsonify({"status": "stopping_requested"})

if __name__ == '__main__':
    port = int(os.environ.get("RUNNER_PORT", 5001))
    print(f"[Runner Microservice] Starting worker server on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
