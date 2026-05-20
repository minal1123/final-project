# Unit tests for input validations
import os
import sys

# Resolve imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from frontend.utils.validation import (
    validate_url, validate_requests, validate_concurrency,
    validate_interval, validate_json_string
)

def test_url_validation():
    # Valid cases
    ok, res = validate_url("http://localhost:5000")
    assert ok is True
    ok, res = validate_url("https://www.google.com/path?query=1")
    assert ok is True
    
    # Invalid cases
    ok, res = validate_url("")
    assert ok is False
    ok, res = validate_url("ftp://some-domain.com")
    assert ok is False
    ok, res = validate_url("not-a-url")
    assert ok is False

def test_request_count_validation():
    # Valid
    ok, res = validate_requests("100")
    assert ok is True
    assert res == 100
    
    # Invalid values
    ok, res = validate_requests("-1")
    assert ok is False
    ok, res = validate_requests("abc")
    assert ok is False
    ok, res = validate_requests("15000") # Cap check
    assert ok is False

def test_concurrency_validation():
    # Valid
    ok, res = validate_concurrency("10", 100)
    assert ok is True
    assert res == 10
    
    # Exceeding total requests
    ok, res = validate_concurrency("50", 10)
    assert ok is False
    
    # Negative/alpha
    ok, res = validate_concurrency("-5", 10)
    assert ok is False
    ok, res = validate_concurrency("abc", 10)
    assert ok is False

def test_interval_validation():
    # Valid
    ok, res = validate_interval("0.5")
    assert ok is True
    assert res == 0.5
    
    # Empty default
    ok, res = validate_interval("")
    assert ok is True
    assert res == 0.0
    
    # Invalid
    ok, res = validate_interval("-0.1")
    assert ok is False
    ok, res = validate_interval("abc")
    assert ok is False

def test_json_string_validation():
    # Valid JSON
    ok, res = validate_json_string('{"Content-Type": "application/json"}', "Headers")
    assert ok is True
    assert res["Content-Type"] == "application/json"
    
    # Empty string
    ok, res = validate_json_string("", "Headers")
    assert ok is True
    assert res == {}
    
    # Invalid JSON
    ok, res = validate_json_string('{"bad_json": }', "Headers")
    assert ok is False
