import requests
import zipfile
import io
import sys

import os
token = os.environ.get('GITHUB_TOKEN', '')
headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}

r = requests.get('https://api.github.com/repos/Sardorr555/landing_swipies/actions/runs?per_page=3', headers=headers)
data = r.json()
for run in data.get('workflow_runs', []):
    print(f"Run #{run['run_number']} id={run['id']} status={run['status']} conclusion={run['conclusion']}")

latest = data['workflow_runs'][0]
run_id = latest['id']
print(f'\nFetching logs for run {run_id}...')
r2 = requests.get(f'https://api.github.com/repos/Sardorr555/landing_swipies/actions/runs/{run_id}/logs', headers=headers)
if r2.status_code == 200:
    z = zipfile.ZipFile(io.BytesIO(r2.content))
    print("Files in zip:", z.namelist())
    for fname in z.namelist():
        if 'deploy' in fname.lower() or 'Deploy' in fname:
            print(f'=== {fname} ===')
            content = z.read(fname).decode('utf-8', errors='ignore')
            # Print last 5000 chars (where errors usually are)
            print(content[-5000:])
else:
    print(f"Failed to download logs: {r2.status_code}")
    # Try individual jobs
    jobs_r = requests.get(f'https://api.github.com/repos/Sardorr555/landing_swipies/actions/runs/{run_id}/jobs', headers=headers)
    if jobs_r.status_code == 200:
        jobs = jobs_r.json()
        for job in jobs.get('jobs', []):
            print(f"Job: {job['name']} status={job['status']} conclusion={job['conclusion']}")
            for step in job.get('steps', []):
                print(f"  Step: {step['name']} conclusion={step.get('conclusion')} number={step.get('number')}")
