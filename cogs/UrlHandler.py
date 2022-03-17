from youtube_dl import YoutubeDL as youtubedl
from bs4 import BeautifulSoup as bs

import requests
import re

class url_exec():
    def get_video_info(url):
        r = requests.get(url)
        s = bs(r.text, "html.parser")
        title = s.find('title').get_text().replace(' - YouTube', '')
        return title

    def ytdl(url):
        ydl_opts = {
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'format': 'bestaudio',
            'agelimit': '20',
            'noplaylist': 'True',
            'default_search': 'auto',
            'audioformat': 'aac'
        }
        with youtubedl(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                url = info['entries'][-1]['webpage_url']
                url2 = info['entries'][0]['formats'][0]['url']
                title = info['entries'][0]['title']
                thumbnail = info['entries'][-1]['thumbnail']
                duration = info['entries'][0]['duration']
            else:
                url2 = info['url']
                title = info['title'] 
                thumbnail = info['thumbnail']
                duration = info['duration']
        m1, s1 = divmod(int(duration), 60)
        if len(str(s1)) == 1:
            s1 = '0' + str(s1)
        duration = '%s:%s' % (m1, s1)
        return url, url2, title, thumbnail, duration

    def request(input):
        r = requests.get("https://www.youtube.com/results?search_query=" + input)
        s = bs(r.text, "html.parser")
        res = re.findall(r"watch\?v=(\S{11})", s.decode())
        return res