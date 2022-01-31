# Discord music bot
A simple music bot using discord.py  
You need to install ffmpeg and add directory into PATH in order to use the bot  
ffmpeg: ```https://www.ffmpeg.org/download.html```
## Usage
- Download:
  - Using git:
    ```
    git clone https://github.com/vietng322611/music-bot-python
    ```
  - Or download by click on "Code" button and click at "Download zip"
- Install python3 (don't use python 3.10, some modules aren't support this yet)
- Note: Remember to tick add to PATH when install
  - Windows: `python --version`
  - *nix (Linux, MacOS): `python3 --version`
  - If your result looks like this, you can use python now:
    ```
    > python3 --version
    Python 3.X.X
    ```
- Extract the zip file you have download earlier and go to the folder you have extracted:
- Here we have:
  - .env: Open this as notepad or your code editor and put your bot token here
  - config.json: You can edit your bot prefix and choose to be update or not
- Modules install:
  - **Windows**: `pip install -r requirements.txt`
  - ***nix**: `python3 -m pip install -r requirements.txt`
- Run bot:
  - **Windows**: `python bot.py`
  - ***nix**: `python3 bot.py`
##
## Libraries in use
- beautifulsoup4
- discord.py
- requests
- youtube_dl
- python-dotenv
- pynacl

## Credit
Creator: vietng322611 (Murasaki Rie)  
