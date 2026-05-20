# Root Orchestrator for API Load Testing Dashboard
import subprocess
import time
import sys
import os

def main():
    print("=" * 70)
    print("            API LOAD TESTING DASHBOARD - RUNTIME ORCHESTRATOR")
    print("=" * 70)
    
    # Get paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_script = os.path.join(base_dir, "backend", "app.py")
    runner_script = os.path.join(base_dir, "runner_service", "app.py")
    frontend_script = os.path.join(base_dir, "frontend", "main.py")
    
    # 1. Spawn Flask backend in background
    print(f"[*] Spawning Flask backend: {sys.executable} backend/app.py")
    backend_proc = subprocess.Popen(
        [sys.executable, backend_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # 2. Spawn Runner Microservice in background
    print(f"[*] Spawning Runner Microservice: {sys.executable} runner_service/app.py")
    runner_proc = subprocess.Popen(
        [sys.executable, runner_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Stagger wait for port binding
    print("[*] Waiting for services to initialize...")
    time.sleep(2.0)
    
    # Check if backend or runner died immediately (e.g. port already in use)
    if backend_proc.poll() is not None:
        print("[!] Error: Flask backend failed to run. Process output:")
        out, _ = backend_proc.communicate()
        print(out)
        sys.exit(1)
        
    if runner_proc.poll() is not None:
        print("[!] Error: Runner microservice failed to run. Process output:")
        out, _ = runner_proc.communicate()
        print(out)
        backend_proc.terminate()
        sys.exit(1)
        
    print("[+] Backend active on http://127.0.0.1:5000/api")
    print("[+] Runner Microservice active on http://127.0.0.1:5001")
    
    # 3. Run Tkinter UI client synchronously
    print(f"[*] Spawning GUI client: {sys.executable} frontend/main.py")
    
    try:
        subprocess.run([sys.executable, frontend_script], check=True)
    except KeyboardInterrupt:
        print("\n[*] Execution interrupted by user.")
    except subprocess.CalledProcessError as e:
        print(f"[!] GUI Client exited with error code {e.returncode}")
    finally:
        # 4. Clean up daemon processes
        print("[*] Terminating Flask API backend process...")
        backend_proc.terminate()
        
        print("[*] Terminating Runner Microservice process...")
        runner_proc.terminate()
        
        try:
            backend_proc.wait(timeout=3)
            print("[+] Backend process exited cleanly.")
        except subprocess.TimeoutExpired:
            print("[!] Timeout expired. Force killing backend...")
            backend_proc.kill()
            
        try:
            runner_proc.wait(timeout=3)
            print("[+] Runner Microservice process exited cleanly.")
        except subprocess.TimeoutExpired:
            print("[!] Timeout expired. Force killing runner microservice...")
            runner_proc.kill()
            
        print("=" * 70)
        print("                 SHUTDOWN COMPLETE. THANK YOU!")
        print("=" * 70)

if __name__ == '__main__':
    main()
