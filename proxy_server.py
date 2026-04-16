import json
import threading
import time
import subprocess
import os
import sys
import pinggy
import proxy
import requests
from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURATION ---
PORT = 8888
USER = os.getenv("PROXY_USER", "admin")
PASS = os.getenv("PROXY_PASS", "1111")
ANONYMOUS = os.getenv("ANONYMOUS", "true").lower() == "true"
TRAFFIC_LOGGING = os.getenv("TRAFFIC_LOGGING", "false").lower() == "true"
MAX_RUNTIME = os.getenv("MAX_RUNTIME", "3600")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
try:
    MAX_RUNTIME = int(MAX_RUNTIME)
except:
    MAX_RUNTIME = 3600
START_TIME = int(time.time())
END_TIME= START_TIME + MAX_RUNTIME
PUBLIC_IP = "0.0.0.0"

def send_webhook(data):
    if not WEBHOOK_URL: 
        return
    def task():
        try:
            response = requests.post(
                WEBHOOK_URL, 
                json=data,
                timeout=10
            )
            if response.status_code == 200:
                print("[+] Webhook sent successfully!")
            else:
                print(f"[-] Webhook failed with status: {response.status_code}")
        except Exception as e:
            print(f"[!] Error sending webhook: {e}")
    thread = threading.Thread(target=task)
    thread.daemon = True
    thread.start()

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
    retry = 0
    while True:
        print("--- Connecting to Pinggy via SDK ---")

        try:
            # Start tunnel
            tunnel = pinggy.start_tunnel(
                forwardto=f"localhost:{PORT}",
                type="tcp"
            )

            # Pinggy returns list URLs
            urls = tunnel.urls

            if not urls:
                raise Exception("No URLs returned from Pinggy")
            tcp_url = None
            print(urls)
            for url in urls:
                if url.startswith("tcp://"):
                    tcp_url = url
                    break
            if not tcp_url:
                # fallback
                tcp_url = urls[0]

            # Parse host + port
            if "://" in tcp_url:
                tcp_url = tcp_url.split("://")[1]

            host, port = tcp_url.split(":")
            port = int(port)
            
            PUBLIC_IP = get_public_url()
            if PUBLIC_IP:
                print(f"Current IP: {PUBLIC_IP}")

            print("\n" + "*" * 25)
            print("  SUCCESS! TUNNEL CREATED")
            print(f"  PUBLIC HOST : {host}")
            print(f"  PUBLIC PORT : {port}")
            if not ANONYMOUS:
                print(f"  AUTH        : {USER}:{PASS}")
            print("*" * 25 + "\n")

            # Save JSON
            proxy_json = {
                "host": host,
                "port": port,
                "auth": None if ANONYMOUS else {
                    "username": USER,
                    "password": PASS
                },
                "ip": PUBLIC_IP,
                "start_time": START_TIME,
                "end_time": END_TIME
            }
            send_webhook(proxy_json)
            with open("pinggy_tunnel_info.json", "w") as f:
                json.dump(proxy_json, f, indent=4)

            # keep tunnel alive
            while True:
                if not tunnel.is_active():
                    print("[!] Tunnel is down. Attempting to reconnect...")
                    break
                time.sleep(5)

        except KeyboardInterrupt:
            print("KeyboardInterrupt received")
            break

        except Exception as e:
            print(f"[!] Pinggy error: {e}")
            print("Retrying in 15s...\n")
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
    # 1. Timer
    if MAX_RUNTIME > 0:
        threading.Thread(target=lambda: (time.sleep(MAX_RUNTIME), os._exit(0)), daemon=True).start()
    
    # 2. Start Aggressive Tunnel Thread
    threading.Thread(target=start_pinggy_tunnel, daemon=True).start()
    
    # 3. Start Proxy Engine
    run_proxy_native()

if __name__ == "__main__":
    main()