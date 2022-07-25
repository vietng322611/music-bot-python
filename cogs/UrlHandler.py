from youtube_dl import YoutubeDL as youtubedl
from bs4 import BeautifulSoup as bs

import requests
import re

def get_video_info(url) -> str:
    '''
        Return video title
    '''
    r = requests.get(url)
    s = bs(r.text, "html.parser")
    title = s.find('title').get_text().replace(' - YouTube', '')
    return title

def search(opt, input) -> str:
    r = requests.get("https://www.youtube.com/results?search_query=" + input)
    s = bs(r.text, "html.parser")
    if opt == 'one':
        res = re.search(r"watch\?v=(\S{11})", s.decode())
        return res
    elif opt == 'all':
        res = re.findall(r"watch\?v=(\S{11})", s.decode())
        return res

def ytdl(url) -> set:
    if not url.startswith(('https://www.youtube.com/watch?v=', 'https://youtu.be/', 'www.youtube.com/watch?v=', 'youtu.be/')):
        url = 'https://www.youtube.com/' + search('one', url)[0]
    ydl_opts = {
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'aac',
            'preferredquality': '192',
        }],
        'format': 'bestaudio',
        'agelimit': '20',
        'noplaylist': 'True',
        'default_search': 'auto'
    }
    with youtubedl(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        title = info['title'] 
        thumbnail = info['thumbnail']
        duration = info['duration']
    m1, s1 = divmod(int(duration), 60)
    if len(str(s1)) == 1:
        s1 = '0' + str(s1)
    duration = '%s:%s' % (m1, s1)
    return url, url2, title, thumbnail, duration