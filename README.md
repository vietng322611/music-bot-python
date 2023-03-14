# Discord music bot
A simple music bot using discord.py  
You need to install ffmpeg and add ffmpeg's directory into PATH in order to use the bot  
ffmpeg: ```https://www.ffmpeg.org/download.html```
## Usage
- Download:
  - Using git:
    ```
    git clone https://github.com/vietng322611/music-bot-python
    ```
  - Or download by click on "Code" button and click at "Download zip"
- Install python3 (recommended python 3.9 for less error)
- Note: Remember to tick add to PATH when install
  - Windows: `python --version`
  - *nix (Linux, MacOS): `python3 --version`
  - If your result looks like this, you can use python now:
    ```
    > python3 --version
    Python 3.X.X
    ```
- Extract the zip file you have downloaded earlier and go to the folder you have extracted:
- Here we have:
  - .env: Open this as notepad or your code editor and put your bot token here
  - config.json: Contains bot configuration
- Modules install:
  - **Windows**: `pip install -r requirements.txt`
  - ***nix**: `python3 -m pip install -r requirements.txt`
- Run bot:
  - Navigate to the directory first using: `cd [directory]`
  - **Windows**: `python main.py`
  - ***nix**: `python3 main.py`
- How to use config file:
  - "Check_Update_On_Start": Set this to False if you don't want to update
  - "Prefix": Bot prefix, default is !!
  - "Creator_Id": If you are the host, you should change this into yours
  - "Banned_Words": Ban words wordlist
  - "Voice_Greetting": Enter anything you want but remember the "{0}" for member name
  - "gg_Command_lang": For adjust language
##
## Libraries in use
- beautifulsoup4
- discord.py>=1.7.3
- requests
- youtube_dl>=2021.12.17
- python-dotenv
- pynacl
- gtts
- aiohttp(>=3.6.2, <3.8.0)
## Note
If you have problems with your bot try updating to the latest release or DM me your issues via discord  
## Credit
Creator: vietng322611 (murasaki#1843)  
