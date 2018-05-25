import csv
import requests
import shutil
import os.path

path = '/Volumes/AGENTCASHEW/sound-effects/'


def download_file(url):
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(path+local_filename, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

    return local_filename


with open('bbc_sound_effect_source.csv') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:

    if os.path.isfile(f"{path}{row['location']}"):
      continue

    print(f"http://bbcsfx.acropolis.org.uk/assets/{row['location']}")
    download_file(f"http://bbcsfx.acropolis.org.uk/assets/{row['location']}")




