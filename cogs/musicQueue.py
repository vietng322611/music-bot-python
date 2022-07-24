from youtube_dl import YoutubeDL as youtubedl

class get_song():
    def __init__(self, url, title, thumbnail_url):
        self.url = url.strip()
        self.title = title
        self.thumbnail_url = thumbnail_url

    def getPlayer(self):
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
        self.queue = args[0]
        self.url = args[1]
        self.title = args[2]
        self.user = args[3]
        self.avatar = args[4]
        self.thumbnail = args[5]
        self.duration = args[6]

class Queue():
    def __init__(self):
        self.queue = []

    def add(self, *args) -> queue_info:
        '''
            Add song to queue and return added queue object.
        '''
        self.queue.append(queue_info(args))
        return self.queue[-1]

    def clear(self) -> None:
        '''
            Clear the queue.
        '''
        self.queue.clear()
        return

    def pop(self, *pos: int) -> queue_info:
        '''
            Delete queue at position x, default first.
            Return deleted queue object.
            Argument: position(int).
        '''
        if len(pos) == 0: pos = 0
        elif len(pos) > 1: raise TypeError('pop expected at most 1 argument, got 2')
        else: pos = pos[0]
        return self.queue.pop(pos)

    def is_empty(self) -> bool:
        '''
            Return true if queue is empty.
        '''
        return len(self.queue) == 0
    
    def size(self) -> int:
        '''
            Return queue length
        '''
        return len(self.queue)