# SQLite database management for Flask backend
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "load_tests.db")

def get_db_connection():
    """Opens a connection to SQLite and configures it to return Row objects."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Test Runs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            method TEXT NOT NULL,
            total_requests INTEGER NOT NULL,
            success_count INTEGER NOT NULL,
            failure_count INTEGER NOT NULL,
            avg_response_time REAL NOT NULL,
            min_response_time REAL NOT NULL,
            max_response_time REAL NOT NULL,
            requests_per_second REAL NOT NULL,
            timestamp TEXT NOT NULL
        );
    """)
    
    # Test Details table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            request_index INTEGER NOT NULL,
            status_code INTEGER,
            response_time REAL NOT NULL,
            success INTEGER NOT NULL,
            error_message TEXT,
            FOREIGN KEY (run_id) REFERENCES test_runs(id) ON DELETE CASCADE
        );
    """)
    
    conn.commit()
    conn.close()

def save_test_run(run_metrics: dict, request_details: list[dict]) -> int:
    """Saves a run summary and details in a transaction. Returns the run ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        timestamp = run_metrics.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        cursor.execute("""
            INSERT INTO test_runs (
                url, method, total_requests, success_count, failure_count,
                avg_response_time, min_response_time, max_response_time,
                requests_per_second, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_metrics["url"],
            run_metrics["method"],
            run_metrics["total_requests"],
            run_metrics["success_count"],
            run_metrics["failure_count"],
            run_metrics["avg_response_time"],
            run_metrics["min_response_time"],
            run_metrics["max_response_time"],
            run_metrics["requests_per_second"],
            timestamp
        ))
        
        run_id = cursor.lastrowid
        
        detail_inserts = []
        for detail in request_details:
            detail_inserts.append((
                run_id,
                detail["request_index"],
                detail.get("status_code"),
                detail["response_time"],
                1 if detail["success"] else 0,
                detail.get("error_message")
            ))
            
        cursor.executemany("""
            INSERT INTO test_details (
                run_id, request_index, status_code, response_time, success, error_message
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, detail_inserts)
        
        conn.commit()
        return run_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_test_runs() -> list[dict]:
    """Returns all test runs summary."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_runs ORDER BY id DESC")
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results

def get_test_run(run_id: int) -> dict | None:
    """Returns a specific test run summary."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    result = dict(row) if row else None
    conn.close()
    return result

def get_test_run_details(run_id: int) -> list[dict]:
    """Returns individual requests details for a run."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_details WHERE run_id = ? ORDER BY request_index ASC", (run_id,))
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results

def delete_test_run(run_id: int) -> bool:
    """Deletes a test run by ID. Cascades details deletion."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM test_runs WHERE id = ?", (run_id,))
        conn.commit()
        success = cursor.rowcount > 0
        return success
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_aggregate_stats() -> dict:
    """Calculates overall metrics for dashboard dashboard stats."""
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {
        "total_runs": 0,
        "total_requests": 0,
        "success_rate": 100.0,
        "overall_avg_response": 0.0,
        "top_url": "N/A"
    }
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_runs,
                SUM(total_requests) as total_requests,
                SUM(success_count) as total_success,
                AVG(avg_response_time) as overall_avg_response
            FROM test_runs
        """)
        row = cursor.fetchone()
        if row and row["total_runs"] and row["total_runs"] > 0:
            stats["total_runs"] = row["total_runs"]
            stats["total_requests"] = row["total_requests"] or 0
            total_success = row["total_success"] or 0
            
            if stats["total_requests"] > 0:
                stats["success_rate"] = round((total_success / stats["total_requests"]) * 100, 2)
                
            stats["overall_avg_response"] = round(row["overall_avg_response"] or 0.0, 4)
            
            cursor.execute("""
                SELECT url, COUNT(*) as count 
                FROM test_runs 
                GROUP BY url 
                ORDER BY count DESC 
                LIMIT 1
            """)
            url_row = cursor.fetchone()
            if url_row:
                stats["top_url"] = url_row["url"]
    except Exception as e:
        print(f"Error querying aggregate stats: {e}")
    finally:
        conn.close()
    return stats
