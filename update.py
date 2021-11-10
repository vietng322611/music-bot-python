import requests
from zipfile import ZipFile
import time
import urllib
import os

def update(config):
   release = config["Release"].strip("v")
   url = "https://api.github.com/repos/vietng322611/music-bot-python/releases/latest"
   response = requests.get(url)
   if response.status_code != 200:
      print("Can't fetch latest release, abort")
   else:
      latest_release = response.json()["tag_name"].strip("v")
      if float(release) < float(latest_release):
         print(f'Downloading release: {latest_release}')
         package_url = response.json()["assets"][0]["browser_download_url"]
         urllib.request.urlretrieve(package_url, "./bot-project.rar")
         with ZipFile("bot-project.rar", 'r') as zip:
            zip.extractall("./")
         os.remove("bot-project.rar")
         print('Update is done')
      else:
         print("This is the latest release")
   time.sleep(2)
   return