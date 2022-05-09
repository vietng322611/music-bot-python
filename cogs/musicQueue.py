from youtube_dl import YoutubeDL as youtubedl

class musicQueue():
    def __init__(self, url, title, thumbnail_url):
        self.url = url.strip()
        self.title = title
        self.thumbnail_url = thumbnail_url

    def getPlayer(self):
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
            info = ydl.extract_info(self.url, download=False)
            url2 = info['url']
            duration = info['duration']
        return url2, duration