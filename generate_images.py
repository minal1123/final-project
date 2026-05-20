import os
import zlib
import base64
import json
import requests
import time

# Create output folder
OUTPUT_DIR = r"c:\Users\pc\final-project\artifacts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 8 UML Diagram definitions
DIAGRAMS = {
    "use_case_diagram": """graph LR
    %%{init: {
      'theme': 'base',
      'themeVariables': {
        'primaryColor': '#ffffff',
        'primaryTextColor': '#000000',
        'primaryBorderColor': '#000000',
        'lineColor': '#000000',
        'actorBorder': '#000000',
        'actorBackground': '#ffffff'
      },
      'flowchart': { 'curve': 'linear' }
    }}%%
    
    subgraph System ["API Load Testing System Boundary"]
        UC1(["Login"])
        UC2(["Enter API URL"])
        UC3(["Select Request Method"])
        UC4(["Start Load Test"])
        UC5(["Stop Load Test"])
        UC6(["View Analytics"])
        UC7(["View Charts"])
        UC8(["View Test History"])
        UC9(["Delete History"])
        UC10(["Export Reports"])
        UC11(["Manage Settings"])
        UC12(["Handle Errors"])
    end
    
    User((User))
    Admin((Admin))
    
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC8
    User --> UC10
    User --> UC11
    
    Admin --> UC1
    Admin --> UC8
    Admin --> UC9
    Admin --> UC11
    
    UC4 -.->|includes| UC12
    UC4 -.->|includes| UC6
    UC6 -.->|extends| UC7""",

    "class_diagram": """classDiagram
    %%{init: {
      'theme': 'base',
      'themeVariables': {
        'primaryColor': '#ffffff',
        'primaryTextColor': '#000000',
        'primaryBorderColor': '#000000',
        'lineColor': '#000000'
      }
    }}%%

    class User {
        +int id
        +string username
        +string email
        +login() bool
        +logout()
    }
    class Authentication {
        +sessionToken string
        +authenticate(username, password) bool
    }
    class Dashboard {
        +refreshStats()
        +displayMetrics()
    }
    class APIRequest {
        +string url
        +string method
        +dict headers
        +string body
        +validate() bool
    }
    class LoadTester {
        +int totalRequests
        +int concurrency
        +float interval
        +startTest()
        +stopTest()
        +getLiveProgress() dict
    }
    class Analytics {
        +float avgResponseTime
        +float minResponseTime
        +float maxResponseTime
        +float requestsPerSecond
        +calculateStats(details)
    }
    class ChartManager {
        +renderLineChart(data)
        +renderPieChart(data)
        +renderHistogram(data)
    }
    class TestHistory {
        +listAllRuns() list
        +loadRunDetails(runId) dict
        +deleteRun(runId) bool
    }
    class DatabaseManager {
        -string dbPath
        +saveRun(metrics, details) int
        +fetchRun(runId) dict
        +deleteRun(runId) bool
        +getStats() dict
    }
    class ErrorHandler {
        +logError(errorMsg)
        +displayFriendlyError(errorMsg)
    }

    User --> Authentication : uses
    User --> Dashboard : views
    Dashboard --> APIRequest : configures
    Dashboard --> TestHistory : views
    APIRequest --> LoadTester : runs
    LoadTester --> Analytics : generates
    Analytics --> ChartManager : visualizes
    LoadTester --> DatabaseManager : persists
    TestHistory --> DatabaseManager : queries
    LoadTester --> ErrorHandler : delegates-to""",

    "sequence_diagram": """sequenceDiagram
    %%{init: {
      'theme': 'base',
      'themeVariables': {
        'actorBorder': '#000000',
        'actorBkg': '#ffffff',
        'activationBorderColor': '#000000',
        'lineColor': '#000000'
      }
    }}%%
    
    autonumber
    actor User
    participant Frontend as React UI
    participant Backend as Flask REST API
    participant Tester as LoadTester Engine
    participant DB as SQLite Database
    participant Analytics as Analytics Module

    User->>Frontend: Enter URL, concurrency & click "Start"
    Frontend->>Frontend: Validate URL & fields client-side
    Frontend->>Backend: POST /api/test/start (JSON config)
    Backend->>Tester: Initialize LoadTester (spawn ThreadPoolExecutor)
    Backend-->>Frontend: Return 202 Accepted (task_id)
    
    activate Tester
    loop Run Concurrent Tasks
        Tester->>Tester: Dispatch concurrent HTTP queries
        Tester-->>Tester: Log code, response time & status
    end
    deactivate Tester
    
    loop Dynamic Progress Polling (200ms)
        Frontend->>Backend: GET /api/test/status/{task_id}
        Backend->>Tester: Retrieve metrics queue snapshot
        Tester-->>Backend: Snapshot data
        Backend-->>Frontend: Progress JSON & Console logs
        Frontend->>Frontend: Render progress bar & logs console
    end
    
    Tester->>Analytics: Calculate aggregate details
    Analytics-->>Tester: Summarized aggregates
    Tester->>DB: Save metrics summary & telemetry grid
    DB-->>Tester: Save complete transaction
    
    Frontend->>Backend: GET /api/history/{id} (Final fetch)
    Backend->>DB: Query finalized datasets
    DB-->>Backend: SQLite datasets
    Backend-->>Frontend: Return final payload
    
    Frontend->>Analytics: Send dataset to Chart.js
    Analytics-->>Frontend: Render Line, Pie, & Scatter canvases
    Frontend-->>User: Refresh Dashboard with interactive charts""",

    "activity_diagram": """graph TD
    %%{init: {
      'theme': 'base',
      'themeVariables': {
        'primaryColor': '#ffffff',
        'primaryTextColor': '#000000',
        'primaryBorderColor': '#000000',
        'lineColor': '#000000'
      },
      'flowchart': { 'curve': 'linear' }
    }}%%

    Start([Start]) --> Input[Enter URL, Method, Concurrency, and Interval]
    Input --> Validate{Is Input Valid?}
    
    Validate -->|No| ShowError[Show Validation Toast Alert] --> Input
    Validate -->|Yes| StartBackend[Send POST /api/test/start to Flask]
    
    StartBackend --> RunThreads[Spawn Concurrent Worker Thread Pool]
    RunThreads --> LoopRequests[Dispatch HTTP Request batch]
    LoopRequests --> Collect[Receive HTTP Response codes]
    
    Collect --> IsStopped{User clicked Stop?}
    IsStopped -->|Yes| Abort[Abort Remaining Threads] --> SaveData
    IsStopped -->|No| IsFinished{All requests finished?}
    
    IsFinished -->|No| LoopRequests
    IsFinished -->|Yes| SaveData
    
    SaveData[Calculate Aggregates & Start SQLite Transaction] --> DBConfirm{Save Successful?}
    
    DBConfirm -->|No| LogErr[Log Write Error to database log] --> Display
    DBConfirm -->|Yes| Display[Refresh metrics cards & Chart.js graphs]
    
    Display --> End([End])""",

    "state_machine_diagram": """stateDiagram-v2
    %%{init: {
      'theme': 'base',
      'themeVariables': {
        'lineColor': '#000000'
      }
    }}%%

    [*] --> Idle
    Idle --> WaitingForInput : User opens testing view
    WaitingForInput --> WaitingForInput : Modifying inputs
    WaitingForInput --> TestingStarted : Clicks "Start" [Valid config]
    WaitingForInput --> ErrorState : Clicks "Start" [Invalid config]
    
    ErrorState --> WaitingForInput : User resets inputs
    
    state TestingStarted {
        [*] --> SendingRequests
        SendingRequests --> ReceivingResponses : HTTP Handshake
        ReceivingResponses --> SendingRequests : Remaining requests > 0
    }
    
    TestingStarted --> GeneratingAnalytics : Run completes / Stop signal sent
    TestingStarted --> ErrorState : Target host unreachable / Network loss
    
    GeneratingAnalytics --> SavingResults : Math aggregates compiled
    SavingResults --> Completed : DB transaction committed successfully
    SavingResults --> ErrorState : SQLite disk locked / Write error
    
    Completed --> Idle : Navigate away
    ErrorState --> Idle : User acknowledges warning""",

    "er_diagram": """erDiagram
    %%{init: {
      'theme': 'base',
      'themeVariables': {
        'primaryColor': '#ffffff',
        'primaryBorderColor': '#000000',
        'lineColor': '#000000'
      }
    }}%%

    USER ||--o{ API_TEST : executes
    API_TEST ||--|| ANALYTICS : summarizes
    API_TEST ||--o{ TEST_HISTORY : logs-detail
    API_TEST ||--o{ ERROR_LOG : traces

    USER {
        int id PK
        string username
        string email
        string password_hash
    }
    API_TEST {
        int id PK
        int user_id FK
        string url
        string method
        string timestamp
        int total_requests
    }
    ANALYTICS {
        int id PK
        int test_id FK
        float avg_response_time
        float min_response_time
        float max_response_time
        float requests_per_second
        int success_count
        int failure_count
    }
    TEST_HISTORY {
        int id PK
        int test_id FK
        int request_index
        int status_code
        float response_time
        boolean success
        string error_message
    }
    ERROR_LOG {
        int id PK
        int test_id FK
        string error_timestamp
        string error_message
        string error_stack
    }""",

    "component_diagram": """graph TB
    %%{init: {
      'theme': 'base',
      'themeVariables': {
        'primaryColor': '#ffffff',
        'primaryTextColor': '#000000',
        'primaryBorderColor': '#000000',
        'lineColor': '#000000'
      },
      'flowchart': { 'curve': 'linear' }
    }}%%

    subgraph UI ["Presentation Layer (React Frontend)"]
        Components["React UI Elements"]
        ChartJS["Chart.js Wrapper Module"]
        APIClient["REST Client (Axios/Fetch)"]
        
        Components --> ChartJS
        Components --> APIClient
    end

    subgraph Orchestrator ["Orchestrator Service (Flask Backend - Port 5000)"]
        FlaskRouter["Flask REST Endpoint Controllers"]
        AuthModule["Authentication Module"]
        Gateway["Microservice Gateway Client"]
        ErrService["Exception Error Handler"]

        FlaskRouter --> AuthModule
        FlaskRouter --> Gateway
        Gateway --> ErrService
    end

    subgraph RunnerService ["Runner Microservice (Port 5001)"]
        RunnerApp["Runner API Endpoint"]
        TesterEngine["Load Tester Engine (ThreadPool)"]
        
        RunnerApp --> TesterEngine
    end

    subgraph Storage ["Data Access Layer (SQLite Engine)"]
        DB[(SQLite File database.db)]
        Schema["Relational Schema Model"]
        Schema --> DB
    end

    APIClient -- HTTP JSON REST Requests --> FlaskRouter
    Gateway -- HTTP Proxy Requests --> RunnerApp
    Gateway --> Schema
    ErrService --> Schema""",

    "deployment_diagram": """graph TD
    %%{init: {
      'theme': 'base',
      'themeVariables': {
        'primaryColor': '#ffffff',
        'primaryTextColor': '#000000',
        'primaryBorderColor': '#000000',
        'lineColor': '#000000'
      },
      'flowchart': { 'curve': 'linear' }
    }}%%

    subgraph ClientNode ["User Hardware node"]
        Browser["Chrome/Edge Web Browser (React SPA runtime)"]
    end

    subgraph WebServer ["Static Web Server (Nginx / Vercel Host)"]
        BuildFiles["Static Assets (minified HTML, JS, CSS)"]
    end

    subgraph OrchestratorNode ["Orchestrator Server Node (Port 5000)"]
        FlaskWSGI["Flask Backend API Application (Gunicorn WSGI)"]
        SQLiteDB[(SQLite Database Engine: database.db file)]
    end

    subgraph RunnerNode ["Runner Microservice Node (Port 5001)"]
        RunnerService["Load Tester Worker API (Port 5001)"]
    end

    Browser -- Downloads SPA bundle (HTTP Get) --> BuildFiles
    Browser -- Communicates (HTTPS JSON REST / Port 5000) --> FlaskWSGI
    FlaskWSGI -- Delegates Tasks (HTTP / Port 5001) --> RunnerService
    FlaskWSGI -- Transaction Queries (Local File I/O) --> SQLiteDB"""
}

def encode_mermaid_pako(mermaid_code):
    """Encodes a mermaid string to pakodeflated base64url compatible format."""
    # Ensure correct wrapper structure
    data = {
        "code": mermaid_code,
        "mermaid": {"theme": "default"},
        "updateEditor": False,
        "autoSync": True,
        "updateDiagram": False
    }
    json_str = json.dumps(data)
    
    # Compress with wbits=15
    compressor = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=15)
    compressed = compressor.compress(json_str.encode('utf-8')) + compressor.flush()
    
    # Base64url encoding
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii').rstrip('=')
    return f"pako:{encoded}"

from PIL import Image

def main():
    print("=" * 70)
    print("      UML DIAGRAMS RENDERER - DOWNLOADING PRESENTATION ASSETS")
    print("=" * 70)
    
    url = "https://kroki.io/mermaid/png"
    
    for name, code in DIAGRAMS.items():
        png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
        pdf_path = os.path.join(OUTPUT_DIR, f"{name}.pdf")
        
        # Only fetch if files are missing or if it's one of our updated microservice diagrams
        if os.path.exists(png_path) and os.path.exists(pdf_path) and name not in ["component_diagram", "deployment_diagram"]:
            print(f"[~] Skipping unchanged diagram: {name}")
            continue
            
        print(f"[*] Requesting PNG bytes for: {name}...")
        try:
            r = requests.post(url, data=code.encode('utf-8'), timeout=30)
            if r.status_code == 200:
                png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
                with open(png_path, "wb") as f:
                    f.write(r.content)
                print(f"    [+] Saved PNG to: {png_path}")
                
                # Convert PNG to PDF locally
                pdf_path = os.path.join(OUTPUT_DIR, f"{name}.pdf")
                img = Image.open(png_path)
                img.convert("RGB").save(pdf_path, "PDF")
                print(f"    [+] Saved PDF to: {pdf_path}")
            else:
                print(f"    [!] Failed to get PNG: HTTP {r.status_code} - {r.text[:200]}")
        except Exception as e:
            print(f"    [!] Error processing {name}: {str(e)}")
            
        time.sleep(1) # Polite delay
        
    print("\n[+] Asset generation complete. All files saved to 'artifacts' folder.")
    print("=" * 70)

if __name__ == "__main__":
    main()
