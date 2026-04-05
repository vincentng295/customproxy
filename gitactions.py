import proxy_server
import bridge_workflows
import threading
import time
import os
from github_utils import upload_file

if __name__ == "__main__":
    if os.getenv("BRIDGE_WORKFLOWS", "false").lower() == "true":
        # Run the bridge workflow after 55 minutes to continue the workflow before the 60 minute timeout
        thread_bridge = threading.Timer(55 * 60, bridge_workflows.run)
        thread_bridge.daemon = True
        thread_bridge.start()

    # Run the upload file thread
    def watch_and_upload_proxy_info():
        file = "pinggy_tunnel_info.json"
        token = os.getenv("GITHUB_TOKEN", "")
        repo = os.getenv("GITHUB_REPOSITORY", "") 
        if not token or not repo:
            print("Missing GITHUB_TOKEN or GITHUB_REPO")
            return
        last_mtime = None
        last_uploaded_time = 0
        while True:
            try:
                if os.path.exists(file):
                    mtime = os.path.getmtime(file)
                    if last_mtime is None or mtime != last_mtime:
                        now = time.time()
                        if now - last_uploaded_time > 3:
                            print("File changed or created!")
                            for _ in range(3):
                                try:
                                    upload_file(token, repo, file, "json")
                                    last_uploaded_time = now
                                    break
                                except Exception as e:
                                    print("Upload retry:", e)
                                    time.sleep(2)
                        last_mtime = mtime
            except Exception as e:
                print("Error:", e)
            time.sleep(2)
    thread_upload = threading.Thread(target=watch_and_upload_proxy_info)
    thread_upload.daemon = True  # Set as daemon
    thread_upload.start()

    # Start the proxy server (this will block)
    proxy_server.main()