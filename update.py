import requests
import json
import patoolib
import time
import urllib

url = "https://api.github.com/repos/vietng322611/music-bot-python/releases/latest"
response = requests.get(url)
<<<<<<< HEAD
if response.status_code != 200:
   print("Can't fetch latest version, abort")
   time.sleep(2)
   exit()
=======
>>>>>>> 703b213ece930a1a2374452dce537b5d458d9cd4
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
   patoolib.extract_archive("config.json", outdir='./')
print('Done')
<<<<<<< HEAD
time.sleep(2)
=======
time.sleep(2)
exit()
>>>>>>> 703b213ece930a1a2374452dce537b5d458d9cd4
