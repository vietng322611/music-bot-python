from yt_dlp import YoutubeDL as youtubedl

class get_song():
    def __init__(self, url, title, thumbnail_url):
        self.url = url.strip()
        self.title = title
        self.thumbnail_url = thumbnail_url

    def getPlayer(self) -> set:
        '''
            Return video player and video duration.
        '''
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

class queue_info():
    def __init__(self, *args):
        self.url = args[0]
        self.player = args[1]
        self.title = args[2]
        self.user = args[3]
        self.avatar = args[4]
        self.thumbnail = args[5]
        self.duration = args[6]

class Queue():
    def __init__(self):
        self.queue = []

    async def add(self, url: str, player: str, title: str, user: str, avatar: str, thumbnail: str, duration: str) -> queue_info:
        '''
            Add song to queue and return added queue object.
        '''
        self.queue.append(queue_info(url, player, title, user, avatar, thumbnail, duration))
        return self.queue[-1]

    async def clear(self) -> None:
        '''
            Clear the queue.
        '''
        self.queue.clear()
        return

    async def pop(self, pos: int = 0) -> queue_info:
        '''
            Delete queue at position x and return deleted queue object.

            Parameters

            position: `int`
                Queue position from 0 onwards. Default is first.
        '''
        return self.queue.pop(pos)

    async def is_empty(self) -> bool:
        '''
            Return true if queue is empty.
        '''
        return len(self.queue) == 0
    
    async def size(self) -> int:
        '''
            Return queue length.
        '''
        return len(self.queue)