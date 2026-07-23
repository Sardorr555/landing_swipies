import time
import requests
import zipfile
import io

import os
token = os.environ.get('GITHUB_TOKEN', '')
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

print("Monitoring GitHub Actions Run #146...")
run_id = None
while True:
    try:
        r = requests.get('https://api.github.com/repos/Sardorr555/swipies__ai_/actions/runs', headers=headers)
        if r.status_code == 200:
            data = r.json()
            for run in data.get('workflow_runs', []):
                if run['run_number'] == 146:
                    run_id = run['id']
                    status = run['status']
                    conclusion = run['conclusion']
                    print(f"Status: {status} | Conclusion: {conclusion}")
                    if status == 'completed':
                        print("Run #146 has completed!")
                        break
        if run_id and status == 'completed':
            break
    except Exception as e:
        print("Error:", e)
    time.sleep(15)

if not run_id:
    print("Could not find run #146 id")
    exit(1)

print(f"Downloading logs for run {run_id}...")
# Get logs zip
r = requests.get(f'https://api.github.com/repos/Sardorr555/swipies__ai_/actions/runs/{run_id}/logs', headers=headers)
if r.status_code == 200:
    z = zipfile.ZipFile(io.BytesIO(r.content))
    # Look for the log file of Deploy to EC2 step
    for filename in z.namelist():
        print(f"Found log file: {filename}")
        if 'deploy' in filename.lower() or '2_deploy' in filename.lower() or 'run' in filename.lower() or '1_deploy' in filename.lower():
            content = z.read(filename).decode('utf-8', errors='ignore')
            if "Предоставляем права superuser" in content:
                print("--- DEPLOY LOG SUBSECTION ---")
                lines = content.split('\n')
                idx = -1
                for i, line in enumerate(lines):
                    if "Предоставляем права superuser" in line:
                        idx = i
                        break
                if idx != -1:
                    for line in lines[idx:idx+30]:
                        print(line)
                else:
                    print("Could not find text in log content")
                print("-----------------------------")
else:
    print("Failed to download logs:", r.status_code, r.text)
