# Thread-safe load testing executor for Flask backend
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class BackendLoadTester:
    def __init__(self, url: str, method: str, headers: dict = None, body: dict = None,
                 total_requests: int = 100, concurrency: int = 10, interval: float = 0.0,
                 timeout: float = 10.0):
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.body = body
        self.total_requests = total_requests
        self.concurrency = concurrency
        self.interval = interval
        self.timeout = timeout
        
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        
        # Thread-safe live metrics snapshot
        self.status = "initialized"  # initialized, running, finished, stopped, error
        self.error_message = None
        
        self.completed_count = 0
        self.success_count = 0
        self.failure_count = 0
        
        self.avg_response_time = 0.0
        self.min_response_time = 0.0
        self.max_response_time = 0.0
        self.requests_per_second = 0.0
        
        self.details = []
        self.start_time = None
        self.end_time = None
        self.timestamp = None

    def start(self):
        """Starts the load test execution in a background daemon thread."""
        self.status = "running"
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.start_time = time.perf_counter()
        
        # Run orchestrator in a thread
        t = threading.Thread(target=self._run_load_test, daemon=True)
        t.start()

    def stop(self):
        """Signals cancellation to the running test."""
        self.stop_event.set()

    def get_progress_snapshot(self) -> dict:
        """Returns a thread-safe dictionary snapshot of the current metrics."""
        with self.lock:
            elapsed = 0.0
            if self.start_time:
                if self.end_time:
                    elapsed = self.end_time - self.start_time
                else:
                    elapsed = time.perf_counter() - self.start_time
            
            progress = 0.0
            if self.total_requests > 0:
                progress = (self.completed_count / self.total_requests) * 100
                
            return {
                "status": self.status,
                "progress_percent": round(progress, 1),
                "completed_count": self.completed_count,
                "total_requests": self.total_requests,
                "success_count": self.success_count,
                "failure_count": self.failure_count,
                "avg_response_time": round(self.avg_response_time, 4),
                "min_response_time": round(self.min_response_time, 4),
                "max_response_time": round(self.max_response_time, 4),
                "requests_per_second": round(self.requests_per_second, 2),
                "elapsed_time": round(elapsed, 2),
                "error_message": self.error_message,
                "timestamp": self.timestamp,
                # Slice details to return only what is new or limit response size
                "details_count": len(self.details),
                "details": list(self.details) # Copy of request logs
            }

    def _send_request(self, idx: int) -> dict | None:
        """Performs a single HTTP request."""
        if self.stop_event.is_set():
            return None
            
        headers = self.headers.copy()
        if "User-Agent" not in headers:
            headers["User-Agent"] = "APILoadTestingDashboard/1.0"
            
        start = time.perf_counter()
        
        try:
            req_data = None
            if self.body and self.method in ["POST", "PUT", "DELETE"]:
                req_data = self.body
                
            response = requests.request(
                method=self.method,
                url=self.url,
                headers=headers,
                json=req_data if isinstance(req_data, dict) else None,
                data=req_data if isinstance(req_data, str) else None,
                timeout=self.timeout
            )
            
            latency = time.perf_counter() - start
            status_code = response.status_code
            success = 200 <= status_code < 300
            
            return {
                "request_index": idx + 1,
                "status_code": status_code,
                "response_time": latency,
                "success": success,
                "error_message": None if success else f"HTTP Status {status_code}"
            }
        except requests.Timeout:
            return {
                "request_index": idx + 1,
                "status_code": 408,
                "response_time": time.perf_counter() - start,
                "success": False,
                "error_message": "Request Timeout"
            }
        except requests.ConnectionError:
            return {
                "request_index": idx + 1,
                "status_code": 503,
                "response_time": time.perf_counter() - start,
                "success": False,
                "error_message": "Connection Error"
            }
        except Exception as e:
            return {
                "request_index": idx + 1,
                "status_code": 500,
                "response_time": time.perf_counter() - start,
                "success": False,
                "error_message": f"Error: {type(e).__name__}"
            }

    def _run_load_test(self):
        """Runs the load test and updates metrics in real-time."""
        futures_map = {}
        latencies = []
        
        try:
            with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
                for idx in range(self.total_requests):
                    if self.stop_event.is_set():
                        break
                        
                    future = executor.submit(self._send_request, idx)
                    futures_map[future] = idx
                    
                    if self.interval > 0.0:
                        # Wait in small ticks to be cancellation friendly
                        ticks = int(self.interval / 0.05)
                        for _ in range(max(1, ticks)):
                            if self.stop_event.is_set():
                                break
                            time.sleep(0.05)
                            
                # Collect futures as they complete
                for future in as_completed(futures_map):
                    result = future.result()
                    if result:
                        with self.lock:
                            self.details.append(result)
                            self.completed_count += 1
                            if result["success"]:
                                self.success_count += 1
                            else:
                                self.failure_count += 1
                                
                            latencies.append(result["response_time"])
                            self.avg_response_time = sum(latencies) / len(latencies)
                            self.min_response_time = min(latencies)
                            self.max_response_time = max(latencies)
                            
                            elapsed = time.perf_counter() - self.start_time
                            self.requests_per_second = self.completed_count / elapsed if elapsed > 0 else 0
                            
        except Exception as e:
            with self.lock:
                self.status = "error"
                self.error_message = str(e)
            return

        # Finalize
        with self.lock:
            self.end_time = time.perf_counter()
            if self.stop_event.is_set():
                self.status = "stopped"
            else:
                self.status = "finished"
            
            # Sort final details list by request index
            self.details.sort(key=lambda x: x["request_index"])
