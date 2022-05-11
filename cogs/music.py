from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.embeds import Embed
from discord.colour import Color
from discord.ext import commands
from cogs.UrlHandler import *
from gtts import gTTS
from cogs.musicQueue import musicQueue

import asyncio
import pickle
import json
import os
import requests

class music(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.FFMPEG_OPTS = {'before_options': 
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -headers "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0"', 
        'options': '-vn'}
        self.queue = []
        self.titles = []
        self.url = []
        self.users = []
        self.thumbnails = []
        self.current_song = []
        self.task = []
        self.config = config
        if not os.path.exists('./cogs/queues'):
            os.mkdir('./cogs/queues')

    def create_queue(self, url, url2, title, user, thumbnail, avatar, duration):
        self.queue.append(url2)
        self.titles.append(title)
        self.titles.append(duration)
        self.url.append(url)
        self.thumbnails.append(thumbnail)
        self.users.append(user)
        self.users.append(avatar)
        return

    async def add_to_queue(self, ctx, url, url2, title, user, thumbnail, avatar, duration):
        self.create_queue(url, url2, title, user, thumbnail, avatar, duration)
        embed = Embed(title="**Added To Queue**", color=Color.from_rgb(255, 0, 0))
        embed.add_field(name="**Song Name**", value=f"[{title}]({url})", inline=False)
        embed.add_field(name="**Song Length**", value=f"{duration}", inline=False)
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f"Requested by {user}", icon_url=avatar)
        await ctx.message.channel.send(embed=embed)
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

    async def playing(self, ctx, voice):
        if not voice.is_playing():
            if self.queue != []:
                title = self.titles.pop(0)
                url = self.url.pop(0)
                duration = self.titles.pop(0)
                self.current_song = [title, duration]
                loop = asyncio.get_event_loop()
                embed = Embed(title="**Now Playing**", color=Color.from_rgb(255, 0, 0))
                embed.add_field(name="**Song Name**", value=f"[{title}]({url})", inline=False)
                embed.add_field(name="**Song Length**", value=f"{duration}", inline=False)
                embed.set_thumbnail(url=self.thumbnails.pop(0))
                embed.set_footer(text=f"Requested by {self.users.pop(0)}", icon_url=self.users.pop(0))
                voice.play(FFmpegPCMAudio(self.queue.pop(0), **self.FFMPEG_OPTS), after=lambda x=None: self.task.append(loop.create_task(self.playing(ctx, voice))))
                voice.source = PCMVolumeTransformer(voice.source, volume=1.0)
                await ctx.send(embed=embed)
        return

    @commands.command(name='play', aliases=['p'],help='Play song from url', usage='[url or name]')
    async def play(self, ctx):
        input = ctx.message.content
        voice = ctx.voice_client
        status = ctx.author.voice
        if status == None:
            return await ctx.message.channel.send('Please join a voice channel')
        if input == '!!play' or input == '!!p':
            if self.queue != []:
                if voice != None:
                    await self.playing(ctx, voice)
                else:
                    await status.channel.connect()
                    voice = ctx.voice_client
                    await self.playing(ctx, voice)
            else:
                await ctx.message.channel.send('Usage: !!play [url] or [name]')
            return
        url = "".join(input.split("!!play "))
        channel = status.channel
        if voice != None:
            if voice != channel:
                await voice.move_to(channel)
        else:
            await channel.connect()
        url, url2, title, thumbnail_url, duration = ytdl(url)
        voice = ctx.voice_client
        if not voice.is_playing():
            self.create_queue(url, url2, title, ctx.author.name, thumbnail_url, ctx.author.avatar_url, duration)
            await self.playing(ctx, voice)
        else:
            await self.add_to_queue(ctx, url, url2, title, ctx.author.name, thumbnail_url, ctx.author.avatar_url, duration)
        return

    @commands.command(name='search', help='Search for a song on youtube', usage='[name]')
    async def search(self, ctx):
        input = ctx.message.content
        input = input.strip('!!search ')
        res = search('all', input)
        urls = ''
        for i in range(5):
            urls += str(i) + ':' +  get_video_info('https://www.youtube.com/watch?v=' + res[i]) + '\n'
        embed = Embed(title=f'**Result for "{input}"**', description=urls, color=Color.from_rgb(255, 0, 0))
        await ctx.message.channel.send(embed=embed)
        await ctx.message.channel.send('Please choose a song')
        parameter = None
        while parameter == None:
            parameter = await self.get_message(ctx, ctx.message.author)
        if parameter == "cancel":
            await ctx.message.channel.send('Canceled')
            return 'Cancled'
        url = 'https://www.youtube.com/watch?v=' + res[parameter]
        url, url2, title, thumbnail_url, duration = ytdl(url)
        await self.add_to_queue(ctx, url, url2, title, ctx.author.name, thumbnail_url, ctx.author.avatar_url, duration)
        voice = ctx.guild.voice_client 
        status = ctx.author.voice
        if voice == None:   
            if status == None:
                return
            channel = status.channel
            if voice == None:
                await channel.connect()
            elif voice != channel:
                await voice.move_to(channel)
        voice = ctx.voice_client
        if not voice.is_playing():
            await self.playing(ctx, voice)
        return
    
    @commands.command(name='skip', help='Skip to next song in queue')
    async def skip(self, ctx):
        voice = ctx.voice_client
        status = ctx.author.voice
        if status == None:
            await ctx.message.channel.send('Please join a voice channel and play something')
            return
        elif voice == None or not voice.is_playing():
            await ctx.message.channel.send("I'm not playing anything")
            return
        elif status.channel.id != voice.channel.id:
            await ctx.message.channel.send('Please switch to my current voice channel to use that')
        elif self.queue != []:
            voice.stop()
            await self.playing(ctx, voice)
            return
        else:
            await ctx.message.channel.send('No song left')
        return

    @commands.command(name='vol', help='Change commands volume', usage='!!vol [number from 1 to 100]')
    async def volume(self, ctx):
        input = ctx.message.content.strip('!!vol ')
        voice = ctx.voice_client
        status = ctx.author.voice
        if status == None:
            await ctx.message.channel.send('Please join a voice channel and play something')
            return
        elif voice == None or not voice.is_playing():
            await ctx.message.channel.send("I'm not playing anything")
            return
        elif status.channel.id != voice.channel.id:
            await ctx.message.channel.send('Please switch to my current voice channel to use that')
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

    @commands.command(name='delete', aliases=['d', 'del'],help='Delete a song from queue', usage='[song index]')
    async def delete(self, ctx):
        input = ctx.message.content
        pos = input.strip('!!delete ')
        if pos.isalnum:
            pos = int(pos)
        else:
            await ctx.message.channel.send('Please enter a number')
            return
        try:
            self.queue.pop(pos)
            self.titles.pop(pos)
            self.titles.pop(pos)
            self.url.pop(pos)
            self.thumbnails.pop(pos)
            self.users.pop(pos)
            self.users.pop(pos)
            await ctx.message.channel.send('Deleted from queue')
        except:
            await ctx.message.channel.send('Out of range')
        return

    @commands.command(name='queue', help='Show current songs in queue')
    async def show_queue(self, ctx):
        voice = ctx.voice_client
        title = self.current_song[0]
        duratuion = self.current_song[1]
        embed = Embed(color = Color.from_rgb(255, 0, 0))
        embed.add_field(name="Currently Playing", value=f"{title} [{duratuion}]", inline=False)
        if len(self.queue) == 0:
            if voice.is_playing:
                await ctx.message.channel.send(embed=embed)
            elif voice == None:
                await ctx.message.channel.send('No song left')
            return
        count = 0
        list_queue = ''
        for i in range(0, len(self.titles), 2):
            list_queue += f'{count}: {self.titles[i]} [{self.titles[i+1]}]\n'
            count += 1
        embed.add_field(name="Queued songs", value=list_queue, inline=False)
        return await ctx.message.channel.send(embed=embed)
    
    @commands.command(name='pause', aliases=['resume'], help='Pause/Resume the current song')
    async def pause(self, ctx):
        voice = ctx.voice_client
        status = ctx.author.voice
        if status == None:
            await ctx.message.channel.send('Please join a voice channel and play something')
            return
        elif voice == None:
            await ctx.message.channel.send("I'm not playing anything")
            return
        elif status.channel.id != voice.channel.id:
            await ctx.message.channel.send('Please switch to my current voice channel to use that')
        else:
            if not voice.is_paused():
                voice.pause()
                await ctx.message.channel.send('Player paused')
            else:
                voice.resume()
                await ctx.message.channel.send('Player resumed')
        return
    
    @commands.command(name='stop', aliases=['leave'], help='Stop the current song and clear the queue')
    async def stop(self, ctx):
        voice = ctx.voice_client
        status = ctx.author.voice
        if status == None:
            await ctx.message.channel.send('Please join a voice channel and play something')
            return
        elif voice == None:
            await ctx.message.channel.send("I'm not playing anything")
            return
        elif status.channel.id != voice.channel.id:
            await ctx.message.channel.send('Please switch to my current voice channel to use that')
        else:
            self.queue = []
            self.titles = []
            self.url = []
            self.thumbnails = []
            self.users = []
            voice.stop()
            voice.cleanup()
            await voice.disconnect()
            await ctx.message.channel.send("I've leaved the voice channel")
        return
    
    @commands.command(name='gg', aliases=['g'], help='Text to speech')
    async def gg(self, ctx):
      input = ctx.message.content.strip('!!gg ')
      if input == '':
        await ctx.message.channel.send('Please enter something')
        return
      voice = ctx.voice_client
      status = ctx.author.voice
      if status == None:
        await ctx.message.channel.send('Please join a voice channel')
        return
      elif voice == None:
        await status.channel.connect()
        voice = ctx.voice_client
      elif status.channel.id != voice.channel.id:
        await ctx.message.channel.send('Please switch to my current voice channel to use that')
        return
      if not voice.is_playing():
        tts = gTTS(text=input, lang=self.config["gg_Command_lang"])
        tts.save('gg.mp3')
        voice.play(FFmpegPCMAudio('gg.mp3'))
        voice.source = PCMVolumeTransformer(voice.source, volume=1.5)
      return

    @commands.command(name='join', help='Make bot join a vocie channel')
    async def join(self, ctx):
        voice = ctx.voice_client
        status = ctx.author.voice
        if status == None:
            await ctx.message.channel.send('Please join a voice channel')
        elif voice == None:
            await status.channel.connect()
        elif status.channel.id != voice.channel.id:
            await ctx.message.channel.send("I'm currently in a voice channel")
        return

    @commands.command(name="qplay", aliases=['qp'], help='Play your queue')
    async def qplay(self, ctx):
        try:
           queue = pickle.load(open('./cogs/queues/' + str(ctx.author.id), 'rb'))
        except FileNotFoundError:
            await ctx.message.channel.send('You have no queue, please create a queue first')
            return
        voice = ctx.voice_client
        status = ctx.author.voice
        if status == None:
            return await ctx.message.channel.send('Please join a voice channel')
        channel = status.channel
        if voice != None:
            if voice != channel:
                await voice.move_to(channel)
        else:
            await channel.connect()
        voice = ctx.voice_client
        for url in queue:
            url2, duration = url.getPlayer()
            self.create_queue(url.url, url2, url.title, ctx.author.name, url.thumbnail_url, ctx.author.avatar_url, duration)
        if not voice.is_playing():
            await self.playing(ctx, voice)

    @commands.command(name="cqueue", aliases=['cq'], help='Create a queue')
    async def cqueue(self, ctx):
        input = ctx.message.content.replace('!!cqueue ', "").split(", ")
        if input == '':
            await ctx.message.channel.send('Please enter something')
            return
        urls = []
        for url in input:
            params = {"format": "json", "url": url}
            video = "https://www.youtube.com/oembed"
            with requests.get(video, params=params) as response:
                data = json.loads(response.text)
                title = data['title']
                thumbnail_url = data['thumbnail_url']
            urls.append(musicQueue(url, title, thumbnail_url))
        user = str(ctx.author.id)
        if os.path.exists('./cogs/queues/' + user):
            await ctx.message.channel.send('Do you want to create a new queue or add this to your current queue? (y/n)')
            try:
                parameter = await self.bot.wait_for("message", timeout=15)
                if parameter.author == self.bot.user:
                    return
            except asyncio.TimeoutError:
                await ctx.message.channel.send("I'll see it as no")
                with open('./cogs/queues/' + user, 'rb') as f:
                    queue = pickle.load(f)
                    queue.extend(urls)
                with open('./cogs/queues/' + user, 'wb') as f:
                    pickle.dump(queue, f)
                await ctx.message.channel.send("Added to your current queue")
            if parameter.content.lower() == 'y':
                with open("./cogs/queues/" + user, "wb") as f:
                    pickle.dump(urls, f)
                await ctx.message.channel.send("I have created a new queue for you")
            elif parameter.content.lower() == 'n':
                with open('./cogs/queues/' + user, 'rb') as f:
                    queue = pickle.load(f)
                    queue.extend(urls)
                with open('./cogs/queues/' + user, 'wb') as f:
                    pickle.dump(queue, f)
                await ctx.message.channel.send("Added to your current queue")
        else:
            with open("./cogs/queues/" + user, "wb") as f:
                pickle.dump(urls, f)
        await ctx.message.channel.send("I have created a new queue for you")

    @commands.command(name="lqueue", aliases=['lq'], help='List your queue')
    async def lqueue(self, ctx):
        try:
           queue = pickle.load(open('./cogs/queues/' + str(ctx.author.id), 'rb'))
        except FileNotFoundError:
            await ctx.message.channel.send('You have no queue, please create a queue first')
            return
        embed = Embed(color = Color.from_rgb(255, 0, 0))
        count = 0
        list_queue = ''
        for song in queue:
            list_queue += f'{count}: {song.title}\n'
            count += 1
        embed.add_field(name="Queued songs", value=list_queue, inline=False)
        return await ctx.message.channel.send(embed=embed)

    @commands.command(name="dqueue", aliases=['dq'], help='Delete your queue')
    async def delqueue(self, ctx):
        try:
            queue = pickle.load(open('./cogs/queues/' + str(ctx.author.id), 'rb'))
        except FileNotFoundError:
            await ctx.message.channel.send('You have no queue, please create a queue first')
            return
        queue = []
        pickle.dump(queue, open('./cogs/queues/' + str(ctx.author.id), 'wb'))
        await ctx.message.channel.send("Deleted")
        return

    @commands.command(name="a2queue", aliases=['aq'], help='Add a song to your queue')
    async def a2queue(self, ctx):
        user = str(ctx.author.id)
        try:
            queue = pickle.load(open('./cogs/queues/' + user, 'rb'))
        except FileNotFoundError:
            await ctx.message.channel.send('You have no queue, please create a queue first')
            return
        input = ctx.message.content.replace('!!a2queue ', "").split(", ")
        if input == '':
            await ctx.message.channel.send('Please enter something')
            return
        urls = []
        for url in input:
            params = {"format": "json", "url": url}
            video = "https://www.youtube.com/oembed"
            with requests.get(video, params=params) as response:
                data = json.loads(response.text)
                title = data['title']
                thumbnail_url = data['thumbnail_url']
            urls.append(musicQueue(url, title, thumbnail_url).__dict__)
        with open('./cogs/queues/' + user, 'rb') as f:
            queue = pickle.load(f)
            queue.extend(urls)
        with open('./cogs/queues/' + user, 'wb') as f:
            pickle.dump(queue, f)
        await ctx.message.channel.send("Added to your current queue")
