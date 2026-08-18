import urllib.request
import json
import ssl

url = "https://api.github.com/repos/dearspartan/snapclip/actions/runs"
req = urllib.request.Request(url, headers={"User-Agent": "SnapClipAgent/1.0", "Accept": "application/vnd.github.v3+json"})

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode())
        print(f"Total runs: {data.get('total_count')}")
        for run in data.get('workflow_runs', [])[:5]:
            print(f"ID: {run['id']} | Name: {run['name']} | Status: {run['status']} | Conclusion: {run['conclusion']} | Commit: {run['head_commit']['message'][:40]}")
except Exception as e:
    print(f"Error fetching runs: {e}")
