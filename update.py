# This made by vietng322611, please respect, do not copy without permission, you can change the code inside to your own.

import requests
from zipfile import ZipFile
import time
import urllib
import os
import json

def update(config):
   release = config["Release"].strip("v").strip(".")
   url = config["Update_Url"]
   response = requests.get(url)
   latest_release = response.json()["tag_name"].strip("v").strip(".")
   if response.status_code != 200:
      print("Can't fetch latest release, abort")
   if release < latest_release:
      if response.json()["name"].strip(' ' + latest_release) != "Update":
         print(f"New release avalible, you can download it here: {url.replace('api.', '')}")
      else:
         print(f'New update avalible: {latest_release}')
         print(f'Downloading update: {latest_release.strip("v")}')
         package_url = response.json()["assets"][0]["browser_download_url"]
         urllib.request.urlretrieve(package_url, "./bot-project.zip")
         with ZipFile("bot-project.zip", 'r') as zip:
            zip.extractall("./")
         os.remove("bot-project.zip")
         with open('config.json', 'w') as fp:
            json.dump(config, fp)
         print('Update is done')
   else:
      print('Everything is up to date')
   time.sleep(2)
   return