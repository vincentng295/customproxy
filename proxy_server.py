import json
import threading
import time
import subprocess
import os
import sys
import re
import proxy
import requests

# --- CONFIGURATION ---
PORT = 8888
USER = os.getenv("PROXY_USER", "admin")
PASS = os.getenv("PROXY_PASS", "1111")
ANONYMOUS = os.getenv("ANONYMOUS", "true").lower() == "true"
TRAFFIC_LOGGING = os.getenv("TRAFFIC_LOGGING", "false").lower() == "true"
MAX_RUNTIME = 3600 # 60 minutes

def run_proxy_native():
    print(f"--- Proxy Engine starting on port {PORT} ---")
    try:
        sys.argv = [sys.argv[0], '--hostname', '0.0.0.0', '--port', str(PORT)]
        if ANONYMOUS:
            print("[*] Running in ANONYMOUS mode (no authentication)")
        else:
            sys.argv += ['--basic-auth', f"{USER}:{PASS}"]
            print(f"[*] Authentication enabled")
        if TRAFFIC_LOGGING:
            sys.argv += ['--log-level', 'INFO']
        else:
            sys.argv += ['--log-level', 'CRITICAL']
        proxy.main()
    except Exception as e:
        print(f"[!] Proxy Error: {e}"); os._exit(1)

def start_pinggy_tunnel():
    """
    Reads raw characters to bypass ANSI 'clear screen' and terminal positioning.
    This is the most aggressive way to capture the URL.
    """
    while True:
        print("--- Connecting to Pinggy... (AGGRESSIVE SCANNING) ---")
        
        cmd = [
            "ssh", "-p", "443", "-t", "-t", 
            "-o", "StrictHostKeyChecking=no", 
            "-o", "ServerAliveInterval=30",
            "-o", "ServerAliveCountMax=3",
            "-o", "BatchMode=yes", 
            "-o", "ConnectTimeout=10",
            "-R", f"0:127.0.0.1:{PORT}", "tcp@free.pinggy.io"
        ]
        
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            bufsize=0, # Unbuffered reading
            encoding='utf-8', 
            errors='ignore'
        )

        found_url = False
        buffer = "" # To store incoming characters
        try:
            while True:
                # Read ONE character at a time
                char = process.stdout.read(1)
                if not char: break
                
                buffer += char
                # Keep the buffer small to save memory, but long enough for the URL
                if len(buffer) > 2000:
                    buffer = buffer[-1000:]

                # Search for the pattern in the accumulated buffer
                # This matches the 'rurii-115-73-12-222.run.pinggy-free.link:33877' format
                clean_text = re.sub(r'\x1b\[[0-9;]*[mGKHJKfP]', '', buffer)
                match = re.search(r"([\w-]+\.run\.pinggy-free\.link):(\d{4,5})(?!\d)\s", clean_text)
                
                if match and not found_url:
                    host = match.group(1)
                    remote_port = match.group(2)
                    
                    print("\n" + "*" * 25)
                    print(f"  SUCCESS! TUNNEL CAPTURED")
                    print(f"  PUBLIC HOST : {host}")
                    print(f"  PUBLIC PORT : {remote_port}")
                    if not ANONYMOUS:
                        print(f"  AUTH        : {USER}:{PASS}")
                    print("*" * 25 + "\n")
                    
                    sys.stdout.flush()
                    found_url = True
                    # Write to json file for easy access
                    proxy_json = {
                        "host": host,
                        "port": int(remote_port),
                        "auth": None if ANONYMOUS else {"username": USER, "password": PASS},
                        "start_time": int(time.time())
                    }
                    with open("pinggy_tunnel_info.json", "w") as f:
                        f.write(json.dumps(proxy_json, indent=4))
                    # We don't break, let SSH continue running in the background
        except KeyboardInterrupt:
            print("KeyboardInterrupt received")
            break
        except Exception as e:
            print(f"Error: {e}")
        process.terminate()
        print("Retrying in 15s...")
        time.sleep(15)

def get_public_url():
    # Get ip via ipify
    try:
        ip = requests.get("https://api.ipify.org").text
        return ip
    except Exception as e:
        print(f"[!] Failed to get public IP: {e}")
        return None

def main():
    PRINT_URL = get_public_url()
    if PRINT_URL:
        print(f"Current IP: {PRINT_URL}")

    # 1. Timer
    threading.Thread(target=lambda: (time.sleep(MAX_RUNTIME), os._exit(0)), daemon=True).start()
    
    # 2. Start Aggressive Tunnel Thread
    threading.Thread(target=start_pinggy_tunnel, daemon=True).start()
    
    # 3. Start Proxy Engine
    run_proxy_native()

if __name__ == "__main__":
    main()