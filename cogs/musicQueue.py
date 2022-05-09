from youtube_dl import YoutubeDL as youtubedl

class musicQueue():
    def __init__(self, url, title, thumbnail_url):
        self.url = url.split()
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
        m1, s1 = divmod(int(duration), 60)
        if len(str(s1)) == 1:
            s1 = '0' + str(s1)
        duration = '%s:%s' % (m1, s1)
        return url2, duration