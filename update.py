# This made by vietng322611, please respect, do not copy without permission, you can change the code inside to your own.

import requests
from zipfile import ZipFile
import urllib
import os
import json
import sys

def update(config):
   update = config["Update"].strip("v").strip(".")
   url = config["Update_Url"]
   response = requests.get(url)
   latest_update = response.json()["tag_name"].strip("v").strip(".")
   if response.status_code != 200:
      print("Can't fetch latest release, abort")
   elif response.json()["name"].strip(' ' + 'v' + latest_update) != "Update":
      pass
   elif update < latest_update:
      print(f'New update avalible: {latest_update}')
      print(f'Downloading update: {latest_update.strip("v")}')
      package_url = response.json()["assets"][0]["browser_download_url"]
      urllib.request.urlretrieve(package_url, "./bot-project.zip")
      with ZipFile("bot-project.zip", 'r') as zip:
         while zip.extractall("./"):
            pass
      os.remove("bot-project.zip")
      print('Update is done, restarting bot')
      os.execl(sys.executable, sys.executable, *sys.argv)
   print('Everything is up to date')
   return