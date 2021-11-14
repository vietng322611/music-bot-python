from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands
from youtube_dl import YoutubeDL as youtubedl
from bs4 import BeautifulSoup as bs

import requests
import asyncio
import re

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice = None
        self.ydl_opts = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'options': '-vn'}
        self.queue = []
        self.queue_info = []
    
    def get_video_info(url):
        r = requests.get(url)
        s = bs(r.text, "html.parser")
        title = s.find('title').get_text().replace(' - YouTube', '')
        return title

    def ytdl(self, url):
        with youtubedl(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            title = info['title'] 
        return url2, title

    async def playing(self, ctx, voice):
        if self.queue != []:
            url = self.queue.pop(0)
            title = self.queue_info.pop(0)
            if not voice.is_playing():
                loop = asyncio.get_event_loop()
                voice.play(FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS), after=lambda x=None: loop.create_task(self.playing(ctx, voice)))
                voice.source = PCMVolumeTransformer(voice.source, volume=1.0)
                await ctx.send(f'**Now Playing:** `{title}`')
        return

    @commands.command(name='play', help='Play song from url')
    async def play(self, ctx):
        input = ctx.message.content
        voice = ctx.voice_client  
        status = ctx.author.voice
        if status == None:
            await ctx.message.channel.send('Please join a voice channel')
            return
        if input == '!!play':
            if self.queue != []:
                if voice != None:
                    await self.playing(ctx, ctx.voice_client)
                else:
                    voice = await status.channel.connect()
                    await self.playing(ctx, ctx.voice_client)
                return
        url = input.strip('!!play ')
        if not url.startswith("https://www.youtu") and not url.startswith("https://youtu") and not url.startswith("youtu"):
            await self.search(ctx)
            return
        url2, title = self.ytdl(url)
        self.queue.append(url2)
        self.queue_info.append(title)
        channel = status.channel
        if voice != None:
            if voice != channel:
                voice = await voice.move_to(channel)
        else:
            voice = await channel.connect()
        if not voice.is_playing():
            await self.playing(ctx, voice)
        else:
            await ctx.message.channel.send('Added to queue')
        return

    @commands.command(name='search', help='Search for a song on youtube')
    async def search(self, ctx):
        input = ctx.message.content
        req = input.strip('!!search ')
        r = requests.get("https://www.youtube.com/results?search_query=" + req)
        s = bs(r.text, "html.parser")
        ids = re.findall(r"watch\?v=(\S{11})", s.decode())
        urls = ''
        for i in range(5):
            urls += str(i) + ':' + self.get_video_info('https://www.youtube.com/watch?v=' + ids[i]) + '\n'
        await ctx.message.channel.send('`{}`'.format(urls))
        await ctx.message.channel.send('Please choose a song')
        parameter = None
        while parameter == None:
            parameter = await self.get_message(ctx)
        if parameter == "cancel":
            return await ctx.message.channel.send('Canceled')
        url = 'https://www.youtube.com/watch?v=' + ids[parameter]
        with youtubedl(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            title = info['title']
        self.queue.append(rf'{url2}')
        self.queue_info.append(title)
        await ctx.message.channel.send('I added this to queue: {}'.format(url))
        voice = ctx.voice_client 
        if voice == None:
            status = ctx.author.voice
            if status == None:
                return
            channel = status.channel
            if voice == None:
                voice = await channel.connect()
            else:
                if voice != channel:
                    voice = await voice.move_to(channel)
        if not voice.is_playing():
            await self.playing(ctx, voice)
        return
    
    @commands.command(name='skip', help='Skip to next song in queue')
    async def skip(self, ctx):
        voice = ctx.voice_client 
        if voice == None:
            await ctx.message.channel.send("I'm not playing anything")
        elif self.queue != []:
            voice.stop()
            await self.playing(ctx, voice)
            return
        else:
            await ctx.message.channel.send('No song left')
        return