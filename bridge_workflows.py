import os
import json
import requests

def bridge_workflows(token, bridge_inputs = True):
    repo = os.getenv("GITHUB_REPOSITORY")          # owner/repo
    ref = os.getenv("GITHUB_REF")                  # refs/heads/main
    run_id = os.getenv("GITHUB_RUN_ID")            # current run ID
    event_path = os.getenv("GITHUB_EVENT_PATH")    # path to event.json
    api_base = f"https://api.github.com/repos/{repo}"
    # Step 1: Get current workflow_id using run_id
    run_url = f"{api_base}/actions/runs/{run_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    run_response = requests.get(run_url, headers=headers)
    if run_response.status_code != 200:
        raise Exception(f"Failed to fetch run: {run_response.status_code} - {run_response.text}")
    workflow_id = run_response.json().get("workflow_id")
    if not workflow_id:
        raise Exception("Could not find workflow_id from run.")
    # Step 2: Extract original inputs if available
    inputs = {}
    if bridge_inputs:
        if event_path and os.path.exists(event_path):
            with open(event_path, "r") as f:
                event_data = json.load(f)
                inputs = event_data.get("inputs", {})
    # Step 3: Trigger the workflow again
    dispatch_url = f"{api_base}/actions/workflows/{workflow_id}/dispatches"
    payload = {
        "ref": ref.split("/")[-1],
        "inputs": inputs
    }
    dispatch_response = requests.post(dispatch_url, headers=headers, json=payload)
    if dispatch_response.status_code == 204 or dispatch_response.status_code == 200: # could be 204 No Content or 200 OK
        print(f"Triggered workflow {workflow_id} on branch {payload['ref']}")
    else:
        raise Exception(f"Failed to trigger workflow: {dispatch_response.status_code}")

def run():
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "") 
    bridge_workflows(GITHUB_TOKEN, True)