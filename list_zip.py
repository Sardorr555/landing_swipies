import requests
import zipfile
import io

import os
token = os.environ.get('GITHUB_TOKEN', '')
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

run_id = 29203084712

r = requests.get(f'https://api.github.com/repos/Sardorr555/swipies__ai_/actions/runs/{run_id}/logs', headers=headers)
if r.status_code == 200:
    z = zipfile.ZipFile(io.BytesIO(r.content))
    for filename in z.namelist():
        print(filename)
