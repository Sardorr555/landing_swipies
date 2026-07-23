import requests
import zipfile
import io
import sys

import os
token = os.environ.get('GITHUB_TOKEN', '')
headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}

run_id = 29689552431  # Run #62 that succeeded

r2 = requests.get(f'https://api.github.com/repos/Sardorr555/landing_swipies/actions/runs/{run_id}/logs', headers=headers)
if r2.status_code == 200:
    z = zipfile.ZipFile(io.BytesIO(r2.content))
    print("Files:", z.namelist())
    for fname in z.namelist():
        if '3_Deploy' in fname or 'deploy' in fname.lower():
            print(f'\n=== {fname} ===')
            content = z.read(fname).decode('utf-8', errors='replace')
            # Write to a file so we can read it without encoding issues
            with open('deploy_step_log.txt', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Written to deploy_step_log.txt")
            print("Last 3000 chars:")
            print(content[-3000:])
else:
    print(f"Status: {r2.status_code}")
