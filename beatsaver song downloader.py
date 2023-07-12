import requests
import os
import fnmatch
import json
import zipfile
from pathlib import Path
import re
import sys

CWD = os.path.dirname(os.path.realpath(__file__))

for song_file_name in [f for f in os.listdir(CWD) if (not fnmatch.fnmatch(f, '*.py') and fnmatch.fnmatch(f, '*.*') and not Path(f).is_dir())]:
    original_song_name = ".".join((song_file_name.split("."))[:-1]).replace("'", "")

    song_name = Path(original_song_name).name
    try:
        found = False

        while not found:
            r = requests.get(f'https://beatsaver.com/api/search/text/0?sortOrder=Relevance&q={song_name}', headers={'content-type': 'application/json'})
            response = r.json()
            if r.status_code == 200 and len(response["docs"]) > 0:
                found = True
                break
            r.close()
            new_name = Path(re.sub(r'\s*\(.*\)\s*$', '', song_name)).name
            if new_name == song_name:
                break
            song_name = new_name

        if not found:
            print(f"The song '{original_song_name}' could not be found. Skipping.", file=sys.stderr)
            continue

        version_code = response["docs"][0]["versions"][-1]["hash"]
        response_song_name = response["docs"][0]["name"]

        r.close()

        r = requests.get(f"https://r2cdn.beatsaver.com/{version_code}.zip", stream=True)
        zipfile_name = Path(f"{CWD}/{response_song_name}.zip")
        with open(zipfile_name, 'wb') as f:
            f.write(r.content)
        r.close()

        zip_extract_name = zipfile_name.parent / zipfile_name.stem
        if not os.path.exists(zip_extract_name):
            os.makedirs(zip_extract_name)
        with zipfile.ZipFile(zipfile_name, 'r') as zip_ref:
            zip_ref.extractall(path=zip_extract_name)

        if not os.path.exists(Path(f"{CWD}/__done")):
            os.makedirs(Path(f"{CWD}/__done"))

        zipfile_name.unlink()
        os.rename(Path(f"{CWD}/{song_file_name}"), Path(f"{CWD}/__done/{song_file_name}"))
        print(f"Saving '{song_file_name}' as '{zip_extract_name}'")
    except:
        print(f"There was some issue when trying to process song {original_song_name}. Skipping.", file=sys.stderr)
    

















