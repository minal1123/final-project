# Validation utilities for Tkinter GUI inputs
import re
import json
from urllib.parse import urlparse

def validate_url(url: str) -> tuple[bool, str]:
    if not url:
        return False, "URL cannot be empty."
    url = url.strip()
    if not re.match(r'^https?://', url, re.IGNORECASE):
        return False, "URL must start with http:// or https://"
    try:
        res = urlparse(url)
        if all([res.scheme, res.netloc]):
            return True, url
        return False, "Invalid URL structure."
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"

def validate_requests(requests_str: str) -> tuple[bool, int | str]:
    if not requests_str:
        return False, "Requests count is required."
    try:
        val = int(requests_str)
        if val <= 0:
            return False, "Requests count must be positive."
        if val > 10000:
            return False, "Requests count capped at 10,000 for safety."
        return True, val
    except ValueError:
        return False, "Requests count must be an integer."

def validate_concurrency(concurrency_str: str, max_limit: int) -> tuple[bool, int | str]:
    if not concurrency_str:
        return False, "Concurrency count is required."
    try:
        val = int(concurrency_str)
        if val <= 0:
            return False, "Concurrency must be positive."
        if val > 200:
            return False, "Concurrency capped at 200 workers."
        if val > max_limit:
            return False, f"Concurrency ({val}) cannot exceed total requests ({max_limit})."
        return True, val
    except ValueError:
        return False, "Concurrency must be an integer."

def validate_interval(interval_str: str) -> tuple[bool, float | str]:
    if not interval_str:
        return True, 0.0
    try:
        val = float(interval_str)
        if val < 0.0:
            return False, "Interval cannot be negative."
        if val > 300.0:
            return False, "Interval limit is 300.0 seconds."
        return True, val
    except ValueError:
        return False, "Interval must be a valid float."

def validate_json_string(json_str: str, field_name: str) -> tuple[bool, dict | str]:
    if not json_str or json_str.strip() == "":
        return True, {}
    try:
        parsed = json.loads(json_str.strip())
        if not isinstance(parsed, dict):
            return False, f"{field_name} must be a valid JSON dictionary."
        return True, parsed
    except json.JSONDecodeError as e:
        return False, f"Invalid {field_name} JSON: {str(e)}"
