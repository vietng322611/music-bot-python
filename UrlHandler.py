from youtube_dl import YoutubeDL as youtubedl
from bs4 import BeautifulSoup as bs

import requests
import re

class url_exec():
    def get_thumbnail(url):
        if "watch\?v=" in url:
            thumbnail_url = "https://img.youtube.com/vi/%s/0.jpg" % re.findall(r"watch\?v=(\S{11})", url)[0]
        else:
            thumbnail_url = "https://img.youtube.com/vi/%s/0.jpg" % re.findall(r"/(\S{11})", url)[0]
        return thumbnail_url

    def get_video_info(self, url):
        r = requests.get(url)
        s = bs(r.text, "html.parser")
        title = s.find('title').get_text().replace(' - YouTube', '')
        return title

    def ytdl(url):
        ydl_opts = {'format': 'best', 'noplaylist':'True'}
        with youtubedl(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            title = info['title'] 
        return url2, title

    def request(input):
        r = requests.get("https://www.youtube.com/results?search_query=" + input)
        s = bs(r.text, "html.parser")
        res = re.findall(r"watch\?v=(\S{11})", s.decode())
        return res