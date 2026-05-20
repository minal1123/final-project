# API Client to communicate with Flask backend
import requests
import json

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:5000/api"):
        self.base_url = base_url

    def _get(self, endpoint: str) -> dict:
        """Helper to send GET requests with exception handling."""
        try:
            r = requests.get(f"{self.base_url}{endpoint}", timeout=5.0)
            if r.status_code == 200:
                return r.json()
            else:
                try:
                    err_msg = r.json().get("error", "Unknown server error.")
                except Exception:
                    err_msg = f"HTTP Error {r.status_code}"
                raise Exception(err_msg)
        except requests.ConnectionError:
            raise Exception("Cannot connect to Flask backend server. Ensure the backend is running.")
        except Exception as e:
            raise Exception(f"API Request failed: {str(e)}")

    def _post(self, endpoint: str, payload: dict = None) -> dict:
        """Helper to send POST requests with exception handling."""
        try:
            r = requests.post(f"{self.base_url}{endpoint}", json=payload, timeout=5.0)
            if r.status_code in [200, 201]:
                return r.json()
            else:
                try:
                    err_msg = r.json().get("error", "Unknown server error.")
                except Exception:
                    err_msg = f"HTTP Error {r.status_code}"
                raise Exception(err_msg)
        except requests.ConnectionError:
            raise Exception("Cannot connect to Flask backend server. Ensure the backend is running.")
        except Exception as e:
            raise Exception(f"API Request failed: {str(e)}")

    def _delete(self, endpoint: str) -> dict:
        """Helper to send DELETE requests with exception handling."""
        try:
            r = requests.delete(f"{self.base_url}{endpoint}", timeout=5.0)
            if r.status_code == 200:
                return r.json()
            else:
                try:
                    err_msg = r.json().get("error", "Unknown server error.")
                except Exception:
                    err_msg = f"HTTP Error {r.status_code}"
                raise Exception(err_msg)
        except requests.ConnectionError:
            raise Exception("Cannot connect to Flask backend. Ensure the backend is running.")
        except Exception as e:
            raise Exception(f"API Request failed: {str(e)}")

    def start_test(self, url: str, method: str, requests_count: int, concurrency: int,
                   interval: float, headers: dict = None, body: dict = None) -> str:
        """Triggers a load test run on the backend."""
        payload = {
            "url": url,
            "method": method,
            "requests": requests_count,
            "concurrency": concurrency,
            "interval": interval,
            "headers": headers or {},
            "body": body
        }
        res = self._post("/test/start", payload)
        return res["task_id"]

    def get_test_status(self, task_id: str) -> dict:
        """Fetches progress metrics snapshot for a running/finished task."""
        return self._get(f"/test/status/{task_id}")

    def stop_test(self, task_id: str) -> bool:
        """Stops an active load test."""
        res = self._post(f"/test/stop/{task_id}")
        return res.get("status") == "stopping_requested"

    def get_history(self) -> list[dict]:
        """Gets all test summaries from database."""
        return self._get("/history")

    def get_history_detail(self, run_id: int) -> dict:
        """Gets full details of a specific test run."""
        return self._get(f"/history/{run_id}")

    def delete_history(self, run_id: int) -> bool:
        """Deletes a historical test run."""
        res = self._delete(f"/history/{run_id}")
        return res.get("success", False)

    def get_stats(self) -> dict:
        """Gets aggregate stats for the home dashboard."""
        return self._get("/stats")
