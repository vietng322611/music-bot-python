import requests
import json
import patoolib
import os
import time
import urllib

url = "https://api.github.com/repos/vietng322611/music-bot-python/releases/latest"
response = requests.get(url)
latest_release = response.json()["html_url"].strip("https://github.com/vietng322611/music-bot-python/releases/tag/v")
f = open("../config.json")
current_release = json.load(f)
if current_release["release"].strip('v') < latest_release:
   current_release = latest_release
   print(f'Downloading release: {current_release}')
   assets_url = response.json()["assets_url"]
   package_url = requests.get(assets_url).json()["browser_download_url"]
   urllib.request.urlretrieve(package_url, './')
   patoolib.extract_archive("main.py", outdir='./')
print('Done')
time.sleep(2)
exit()
