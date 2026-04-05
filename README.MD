# Remote Proxy Server

A flexible, high-performance HTTP(S) proxy server that can be deployed instantly via **GitHub Actions** or locally on **Windows/Linux**. It utilizes `proxy.py` for the engine and `Pinggy` to create a secure tunnel, providing you with a public URL even if you are behind a firewall or NAT.

**Repo URL:** `https://github.com/vincentng295/customproxy`

## 🚀 Features
* **GitHub Actions Integration:** Run a proxy for free on GitHub's infrastructure.
* **Automatic Tunneling:** No port forwarding required; provides a public `.pinggy-free.link` address.
* **Authentication:** Supports both Basic Auth (Username/Password) and Anonymous modes.
* **Traffic Logging:** Optional real-time request logging to the console.
* **Cross-Platform:** Works on Linux, Windows, and macOS.

---

## 🛠 Usage: GitHub Actions (Recommended)

This is the easiest way to get a temporary remote proxy without using your own hardware.

1.  Go to the **Actions** tab of your repository.
2.  Select the **Remote Proxy Server** workflow on the left sidebar.
3.  Click the **Run workflow** dropdown.
4.  Configure your settings:
    * **Proxy Username:** (Default: `admin`)
    * **Proxy Password:** (Default: `1111`)
    * **Anonymous mode:** Check to disable authentication.
    * **Traffic logging:** Check to see all URLs being accessed.
5.  Click **Run workflow**.
6.  Wait for the **Run Proxy Server** step. The logs will display your **Public Host** and **Public Port**.

---

## 💻 Local Setup (Linux / Windows)

### Prerequisites
* Python 3.12 or higher.
* SSH Client installed (Native on Windows 10/11 and Linux).

### 1. Clone the Repository
```bash
git clone https://github.com/vincentng295/customproxy.git
cd customproxy
```

### 2. Install Dependencies
```bash
pip install proxy.py requests
```

### 3. Run the Server
You can run the script using default credentials or set environment variables to customize it.

#### **Linux / macOS:**
```bash
# Optional: Set credentials
export PROXY_USER="myuser"
export PROXY_PASS="mypassword"
export ANONYMOUS="false"

python3 proxy_server.py
```

#### **Windows (PowerShell):**
```powershell
# Optional: Set credentials
$env:PROXY_USER="myuser"
$env:PROXY_PASS="mypassword"
$env:ANONYMOUS="false"

python proxy_server.py
```

---

## ⚙️ Configuration Parameters

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PROXY_USER` | `admin` | Username for basic authentication. |
| `PROXY_PASS` | `1111` | Password for basic authentication. |
| `ANONYMOUS` | `false` | If `true`, the proxy will not require a login. |
| `TRAFFIC_LOGGING`| `false` | If `true`, prints all requests to the console. |
| `MAX_RUNTIME` | `3600` | (In script) Auto-shuts down after 60 minutes. |

---

## 🛡 Disclaimer
This tool is intended for educational purposes and personal use. Please ensure you comply with the Terms of Service of GitHub and any network provider you use this on. The authors are not responsible for any misuse.