# This made by vietng322611, please respect, do not copy without permission, you can change the code inside to your own.

import requests
from zipfile import ZipFile
import time
import urllib
import os
import json
import sys

def update_release(latest_release, config, response):
   config["Release"] = latest_release
   package_url = response.json()["assets"][0]["browser_download_url"]
   urllib.request.urlretrieve(package_url, "./bot-project.zip")
   with ZipFile("bot-project.zip", 'r') as zip:
      while zip.extractall("./"):
         pass
      os.remove("bot-project.zip")
   with open('config.json', 'w') as fp:
      json.dump(config, fp)
   print('Update is done, restarting bot')
   time.sleep(2)
   

def update(config):
   update = config["Update"].strip("v").strip(".")
   release = config["Release"].strip("v").strip(".")
   url = config["Update_Url"]
   response = requests.get(url)
   latest_update = response.json()["tag_name"].strip("v").strip(".")
   if response.status_code != 200:
      print("Can't fetch latest release, abort")
   elif response.json()["name"].strip(' ' + 'v' + latest_update) != "Update":
      print(response.json()["name"])
      if release < latest_update:
         print(f"New release avalible, downloading release {latest_update.strip('v')}")
         update_release(latest_update, config, response)
      return
   elif update < latest_update:
      print(f'New update avalible: {latest_update}')
      print(f'Downloading update: {latest_update.strip("v")}')
      package_url = response.json()["assets"][0]["browser_download_url"]
      urllib.request.urlretrieve(package_url, "./bot-project.zip")
      with ZipFile("bot-project.zip", 'r') as zip:
         while zip.extractall("./"):
            pass
         os.remove("bot-project.zip")
      with open('config.json', 'w') as fp:
         json.dump(config, fp)
      print('Update is done, restarting bot')
   else:
      print('Everything is up to date')
   os.execl(sys.executable, sys.executable, *sys.argv)