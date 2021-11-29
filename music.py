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
        self.ydl_opts = {'format': 'bestaudio', 'noplaylist':'True'}
        self.queue = []
        self.queue_info = []
        self.current_voice_channel = None
    def get_video_info(self, url):
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

    def request(self, inp):
        r = requests.get("https://www.youtube.com/results?search_query=" + inp)
        s = bs(r.text, "html.parser")
        res = re.findall(r"watch\?v=(\S{11})", s.decode())
        return res

    async def playing(self, ctx, voice):
        if not voice.is_connected():
            self.current_voice_channel.connect()
        if self.queue != []:
            player = self.queue.pop(0)
            title = self.queue_info.pop(0)
            if not voice.is_playing():
                loop = asyncio.get_event_loop()
                voice.play(FFmpegPCMAudio(player), after=lambda x=None: loop.create_task(self.playing(ctx, voice)))
                voice.source = PCMVolumeTransformer(voice.source, volume=1.0)
                await ctx.send(f'**Now Playing:** `{title}`')
        return

    async def get_message(self, ctx, user):
        try:
            parameter = await self.bot.wait_for("message", timeout=15)
            if parameter.author == self.bot.user:
                return None
        except asyncio.TimeoutError:
            await ctx.channel.send("Sorry, you didn't reply in time!")
            return "cancel"
        if parameter.author != user:
            return None 
        elif parameter.content == "cancel":
            return parameter.content
        elif parameter.content.isnumeric() == True:
            return int(parameter.content)
        else:
            await ctx.message.channel.send('Please enter a number')
        await commands.Cog.process_commands(ctx)
        return None
        
    @commands.command(name='vol', help='Change commands volume')
    async def volume(ctx):
        input = ctx.message.content.strip('!!vol ')
        voice = ctx.voice_client
        status = ctx.author.voice
        if status == None:
            await ctx.message.channel.send('Please join a voice channel and play something')
            return
        elif voice == None:
            await ctx.message.channel.send("I'm not playing anything")
            return
        try:
            input = float(input)
        except ValueError:
            await ctx.message.channel.send('Please enter a number from 0 to 200')
            return
        if input < 0 or input > 200:
            await ctx.message.channel.send('Please enter a number from 0 to 200')
            return
        volume = input / 100
        voice.source.volume = volume
        return await ctx.message.channel.send(f'**Volume changed to** {int(input)}/200')

    @commands.command(name='leave', help='Leave voice channel')
    async def leave(self, ctx):
        voice = ctx.voice_client
        if voice != None:
            if voice.is_playing:
                voice.stop()
                return await voice.disconnect()
        else:
            return await ctx.message.channel.send("I'm not in a voice channel now" )

    @commands.command(name='stop', help='Stop bot playing songs')
    async def stop(self, ctx):
        voice = ctx.voice_client 
        if voice == None:
            await ctx.channel.send("I'm not playing anything")
            return 
        if self.queue == []:
            voice.stop()
            await voice.disconnect()
        else:
            voice.stop()
        await ctx.message.channel.send('Stopped')
        return

    @commands.command(name='delete', help='Delete a song from queue')
    async def delete(self, ctx):
        input = ctx.message.content
        pos = input.strip('!!delete ')
        try:
            pos = int(pos)
        except:
            await ctx.message.channel.send('Please enter a number')
        try:
            self.queue.pop(pos)
            self.queue_info.pop(pos)
            await ctx.message.channel.send('Deleted from queue')
        except:
            await ctx.message.channel.send('Out of range')
        return
    @commands.command(name='show-queue', help='Show current songs in queue')
    async def show_queue(self, ctx):
        if len(self.queue) == 0:
            await ctx.message.channel.send('No song left')
            return
        count = 0
        list_queue = ''
        for i in self.queue_info:
            list_queue += f'{count}:{i}\n'
            count += 1
        return await ctx.message.channel.send(list_queue)

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
                    await self.playing(ctx, voice)
                else:
                    voice = await status.channel.connect()
                    await self.playing(ctx, voice)
                return
        url = input.strip('!!play ')
        if not url.startswith("https://www.youtu") and not url.startswith("https://youtu") and not url.startswith("youtu"):
            url = 'https://www.youtube.com/watch?v=' + self.request(url)[0]
        url2, title = self.ytdl(url)
        self.queue.append(url2)
        self.queue_info.append(title)
        channel = status.channel
        if voice != None:
            if voice != channel:
                voice = await voice.move_to(channel)
        else:
            voice = await channel.connect(reconnect=True)
        self.current_voice_channel = voice
        if not voice.is_playing():
            await self.playing(ctx, voice)
        else:
            await ctx.message.channel.send('Added to queue')
        return

    @commands.command(name='search', help='Search for a song on youtube')
    async def search(self, ctx):
        input = ctx.message.content
        req = input.strip('!!search ')
        res = self.request(req)
        urls = ''
        for i in range(5):
            urls += str(i) + ':' + self.get_video_info('https://www.youtube.com/watch?v=' + res[i]) + '\n'
        await ctx.message.channel.send('`{}`'.format(urls))
        await ctx.message.channel.send('Please choose a song')
        parameter = None
        while parameter == None:
            parameter = await self.get_message(ctx, ctx.message.author)
        if parameter == "cancel":
            return await ctx.message.channel.send('Canceled')
        url = 'https://www.youtube.com/watch?v=' + res[parameter]
        url2, title = self.ytdl(url)
        self.queue.append(url2)
        self.queue_info.append(title)
        await ctx.message.channel.send('I added this to queue: {}'.format(url))
        voice = ctx.guild.voice_client 
        if voice == None:
            status = ctx.author.voice
            if status == None:
                return
            channel = status.channel
            if voice == None:
                voice = await channel.connect(reconnect=True)
            else:
                if voice != channel:
                    voice = await voice.move_to(channel)
        self.current_voice_channel = voice
        if not voice.is_playing():
            await self.playing(ctx, voice)
        return
    
    @commands.command(name='skip', help='Skip to next song in queue')
    async def skip(self, ctx):
        voice = ctx.guild.voice_client
        self.current_voice_channel = voice
        if voice == None:
            await ctx.message.channel.send("I'm not playing anything")
        elif self.queue != []:
            voice.stop()
            await self.playing(ctx, voice)
            return
        else:
            await ctx.message.channel.send('No song left')
        return