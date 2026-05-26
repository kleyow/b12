import os
import json
import hmac
import hashlib
from datetime import datetime, timezone
import urllib.request
import urllib.error

def main():
    # 1. Gather pipeline environment variables
    server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repository = os.environ.get("GITHUB_REPOSITORY", "your-username/your-repo")
    run_id = os.environ.get("GITHUB_RUN_ID", "1234567890")

    repo_link = f"{server_url}/{repository}"
    action_run_link = f"{repo_link}/actions/runs/{run_id}"

    # 2. Build the payload dictionary
    # Python dicts preserve insertion order (Python 3.7+), but sorting keys
    # explicitly guarantees canonical structure during serialization.
    payload = {
        "action_run_link": action_run_link,
        "email": "kleyow@gmail.com",
        "name": "Kevin Leyow",
        "repository_link": repo_link,
        "resume_link": "https://github.com/kleyow/b12/blob/main/Kevin_Leyow_Resume_11052026.pdf",
        "timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace("+00:00", "Z")
    }

    # 3. Canonicalize the JSON (No extra whitespace, keys sorted alphabetically)
    compact_json_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    compact_json_bytes = compact_json_str.encode('utf-8')

    # 4. Compute the HMAC-SHA256 Signature
    secret = b"hello-there-from-b12"
    signature_hash = hmac.new(secret, compact_json_bytes, hashlib.sha256).hexdigest()
    signature_header = f"sha256={signature_hash}"

    # 5. Dispatch HTTP POST Request
    url = "https://b12.io/apply/submission"
    req = urllib.request.Request(
        url,
        data=compact_json_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": signature_header
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            data = json.loads(response_body)

            # 6. Parse and print receipt for CI visibility
            if data.get("success"):
                print("Submission Successful!")
                print(f"Receipt: {data.get('receipt')}")
            else:
                print(f"Unexpected response format: {response_body}")
                exit(1)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_body}")
        exit(1)
    except urllib.error.URLError as e:
        print(f"Failed to reach server: {e.reason}")
        exit(1)

if __name__ == "__main__":
    main()
