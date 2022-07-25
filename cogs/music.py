''' TODO: 
    + Create error handler
'''

from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.embeds import Embed
from discord.colour import Color
from discord.ext import commands
from cogs.UrlHandler import *
from gtts import gTTS
from cogs.musicQueue import *

import asyncio
import pickle
import json
import os
import requests

class music(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.FFMPEG_OPTS = {'before_options': 
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
        'options': '-vn'}
        self.queue = Queue()
        self.current_song = []
        self.task = []
        self.config = config
        if not os.path.exists('./cogs/queues'):
            os.mkdir('./cogs/queues')

    ''' Variables explain:
            + self.config: Contain config object from config file.
            + self.queue: Contain Queue object.
            + self.current_song: For show queue command
            + self.task: Contain async tasks.
            + self.voice: Contain bot voice object.
            + self.status: Contain user voice object.
    '''

    async def add_to_queue(self, ctx, *args):
        '''
            Add song to the queue and send embed message to notify users the song has been added.

            **Parameters**
            
            video url: `str`
            video player url: `str`
            video title: `str`
            request user's name: `ctx.author.name` -> `str`
            video thumbnail url: `str`
            request user's avatar url: `ctx.author.avatar_url` -> `str`
            video duration: `str`
        '''
        queue_object = self.queue.add(args)
        embed = Embed(title="**Added To Queue**", color=Color.from_rgb(255, 0, 0))
        embed.add_field(name="**Song Name**", value=f"[{queue_object.title}]({queue_object.url})", inline=False)
        embed.add_field(name="**Song Length**", value=f"{queue_object.duration}", inline=False)
        embed.set_thumbnail(url=queue_object.thumbnail)
        embed.set_footer(text=f"Requested by {queue_object.user}", icon_url=queue_object.avatar)
        await ctx.message.channel.send(embed=embed)

    async def get_message(self, ctx, user):
        try:
            parameter = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.message.channel, timeout=15.0)
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
        if not voice.is_playing() and not voice.is_paused() and not self.queue.is_empty():
            queue_object = self.queue.pop()
            self.current_song = [queue_object.title, queue_object.duration]
            loop = asyncio.get_event_loop()
            embed = Embed(title="**Now Playing**", color=Color.from_rgb(255, 0, 0))
            embed.add_field(name="**Song Name**", value=f"[{queue_object.title}]({queue_object.url})", inline=False)
            embed.add_field(name="**Song Length**", value=f"{queue_object.duration}", inline=False)
            embed.set_thumbnail(url=queue_object.thumbnail)
            embed.set_footer(text=f"Requested by {queue_object.user}", icon_url=queue_object.avatar)
            voice.play(FFmpegPCMAudio(self.queue.pop(0), **self.FFMPEG_OPTS), after=lambda x=None: self.task.append(loop.create_task(self.playing(ctx, voice))))
            voice.source = PCMVolumeTransformer(voice.source, volume=1.0)
            await ctx.send(embed=embed)

    @commands.command(name='play', aliases=['p'],help='Play song from url', usage='[url or name]')
    async def play(self, ctx, *, url: str):
        voice = ctx.voice_client
        status = ctx.author.voice
        # Check user & bot voice state
        if status == None:
            return await ctx.message.channel.send('Please join a voice channel')
        channel = status.channel
        if voice != None:
            if voice != channel:
                await voice.move_to(channel)
        else:
            await channel.connect()
        url, url2, title, thumbnail_url, duration = ytdl(url) # url2 youtube video player source
        voice = ctx.voice_client # Get bot vc after connect (voice = await channel.connect() somehow doesn't work)
        if not voice.is_playing():
            self.queue.add(url, url2, title, ctx.author.name, thumbnail_url, ctx.author.avatar_url, duration)
            await self.playing(ctx, voice)
        else:
            await self.add_to_queue(ctx, url, url2, title, ctx.author.name, thumbnail_url, ctx.author.avatar_url, duration)

    ''' 
    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            voice = ctx.voice_client
            status = ctx.author.voice
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
    '''

    @commands.command(name='search', help='Search for a song on youtube', usage='[name]')
    async def search(self, ctx, *, name: str):
        res = search('all', name)
        urls = ''
        for i in range(5):
            urls += str(i) + ':' +  get_video_info('https://www.youtube.com/watch?v=' + res[i]) + '\n'
        embed = Embed(title=f'**Result for "{name}"**', description=urls, color=Color.from_rgb(255, 0, 0))
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

    '''
    @search.error
    async def search_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please enter a name")
    '''

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
        elif not self.queue.is_empty():
            voice.stop()
            await self.playing(ctx, voice)
            return
        else:
            await ctx.message.channel.send('No song left')

    @commands.command(name='vol', help='Change commands volume', usage='!!vol [number from 1 to 100]')
    async def volume(self, ctx, volume: int):
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
        if volume < 0 or volume > 200:
            await ctx.message.channel.send('Please enter a number from 0 to 200')
            return
        volume = volume / 100
        voice.source.volume = volume
        return await ctx.message.channel.send(f'**Volume changed to** {int(volume)}/200')

    '''
    @volume.error
    async def volume_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please enter a number")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please enter a number")
    '''

    @commands.command(name='delete', aliases=['d', 'del'],help='Delete a song from queue', usage='[song index]')
    async def delete(self, ctx, idx: int):
        if 0 <= idx < self.queue.size():
            self.queue.pop(idx)
            await ctx.message.channel.send('Deleted from queue')
        else:
            await ctx.message.channel.send('Out of range')

    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please enter song index")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please enter a number")
        
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
        for i in range(0, self.queue.size()):
            list_queue += f'{count}: {self.queue[i].title} [{self.queue[i].url}]\n'
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
            self.queue.clear()
            voice.stop()
            voice.cleanup()
            await voice.disconnect()
            await ctx.message.channel.send("I've leaved the voice channel")
    
    @commands.command(name='gg', aliases=['g'], help='Text to speech')
    async def gg(self, ctx, text: str):
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
            tts = gTTS(text=text, lang=self.config["gg_Command_lang"])
            tts.save('gg.mp3')
            voice.play(FFmpegPCMAudio('gg.mp3'))
            voice.source = PCMVolumeTransformer(voice.source, volume=1.5)

    '''
    @gg.error
    async def gg_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.channel.send('Please enter something')
            return
    '''

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

    @commands.command(name="cqueue", aliases=['create'], help='Create a queue')
    async def cqueue(self, ctx, *urls: str):
        if len(urls) == 0:
            await ctx.message.channel.send('Please enter a url')
            return
        obj = []
        for url in urls:
            params = {"format": "json", "url": url}
            video = "https://www.youtube.com/oembed"
            with requests.get(video, params=params) as response:
                data = json.loads(response.text)
                title = data['title']
                thumbnail_url = data['thumbnail_url']
            obj.append(get_song(url, title, thumbnail_url))
        user = str(ctx.author.id)
        if os.path.exists('./cogs/queues/' + user):
            await ctx.message.channel.send('You already have a queue, do you want to overwrite it? (y/n)')
            try:
                msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.message.channel, timeout=15.0)
            except asyncio.TimeoutError:
                await ctx.message.channel.send('You took too long, cancelling')
                return
            await commands.Cog.process_commands(ctx)
            if msg.content.lower() == 'n':
                await ctx.message.channel.send('Cancelling')
                return
        with open("./cogs/queues/" + user, "wb") as f:
            pickle.dump(obj, f)
        await ctx.message.channel.send("I have created a new queue for you")

    @commands.command(name="showq", aliases=['show'], help='Show your queue')
    async def showq(self, ctx):
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

    @commands.command(name="qdelete", aliases=['del'], help='Delete your queue')
    async def delqueue(self, ctx):
        try:
            queue = pickle.load(open('./cogs/queues/' + str(ctx.author.id), 'rb'))
        except FileNotFoundError:
            await ctx.message.channel.send('You have no queue, please create a queue first')
            return
        await ctx.message.channel.send('You will delete your whole queue, continue at your own risk? (y/n)')
        msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.message.channel, timeout=15.0)
        if msg.content.lower() == 'n':
            await ctx.message.channel.send('Cancelling')
            return
        pickle.dump([], open('./cogs/queues/' + str(ctx.author.id), 'wb'))
        await ctx.message.channel.send("Deleted")

    @commands.command(name="a2queue", aliases=['add'], help='Add song(s) to your queue')
    async def a2queue(self, ctx, *urls: str):
        urls = urls.split(',')
        user = str(ctx.author.id)
        try:
            queue = pickle.load(open('./cogs/queues/' + user, 'rb'))
        except FileNotFoundError:
            await ctx.message.channel.send('You have no queue, please create a queue first')
            return
        if urls == ['']:
            await ctx.message.channel.send('Please enter something')
            return
        obj = []
        for url in urls:
            params = {"format": "json", "url": url}
            video = "https://www.youtube.com/oembed"
            with requests.get(video, params=params) as response:
                data = json.loads(response.text)
                title = data['title']
                thumbnail_url = data['thumbnail_url']
            obj.append(get_song(url, title, thumbnail_url))
        with open('./cogs/queues/' + user, 'rb') as f:
            queue = pickle.load(f)
            queue.extend(obj)
        with open('./cogs/queues/' + user, 'wb') as f:
            pickle.dump(queue, f)
        await ctx.message.channel.send("Added to your current queue")

    @a2queue.error
    async def a2queue_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.channel.send('Please enter a url')

    @commands.command(name="qedit", aliases=['edit'], help='Edit your queue')
    async def qedit(self, ctx, *args: str):
        user = str(ctx.author.id)
        if len(args) == 0:
            await ctx.message.channel.send(
                'options: \n'
                + '1: delete song(s) at position x\n'
                + '2: add a song (at position x (x <= last position + 1))\n'
                + '3: move song position from x to y\n'
            )
            return
        opt = int(args[0])
        if opt < 1 or opt > 3:
            await ctx.message.channel.send(
                'options: \n'
                + '1: delete song(s) at position x\n'
                + '2: add a song (at position x (x <= last position + 1))\n'
                + '3: edit song(s) position from x to y\n'
            )
        if len(args) < 3:
            if opt == 3:
                await ctx.message.channel.send('Please enter the position you want to move to')
        try:
            queue = pickle.load(open('./cogs/queues/' + user, 'rb'))
        except FileNotFoundError:
            await ctx.message.channel.send('You have no queue, please create a queue first')
            return
        if opt == 1:
            if len(args) < 2:
                await ctx.message.channel.send('Please enter the position you want to delete from')
                return
            try: pos = int(args[1])
            except ValueError:
                await ctx.message.channel.send('Please enter a number')
            if len(args) > 3:
                await ctx.message.channel.send('Too much arguments so i only take the first one')
            if 0 <= pos < len(queue):
                queue.pop(pos)
                with open('./cogs/queues/' + user, 'wb') as f:
                    pickle.dump(queue, f)
                await ctx.message.channel.send("Deleted")
            else:
                await ctx.message.channel.send("Position out of range")
            return
        if opt == 2:
            if len(args) <= 3:
                additional = args[1]
                pos = len(queue)
                if not additional.startswith('https://www.youtube.com') and not additional.startswith('https://youtu.be'):
                    await ctx.message.channel.send('Please enter a valid url')
                    return
            if len(args) == 3:
                if not args[2].isdigit():
                    await ctx.message.channel.send('Please enter a valid position')
                    return
                elif int(args[2]) > len(queue):
                    await ctx.message.channel.send('Please enter a valid position')
                    return
                pos = int(args[2])
            if len(args) > 3:
                if not args[2].isdigit():
                    await ctx.message.channel.send('Please enter a valid position')
                    return
                elif int(args[2]) > len(queue):
                    await ctx.message.channel.send('Please enter a valid position')
                    return
                pos = int(args[2])
                await ctx.message.channel.send('Too much arguments so i only take the first two')
            params = {"format": "json", "url": additional}
            video = "https://www.youtube.com/oembed"
            with requests.get(video, params=params) as response:
                data = json.loads(response.text)
                title = data['title']
                thumbnail_url = data['thumbnail_url']
            queue.insert(pos, get_song(additional, title, thumbnail_url))
            with open('./cogs/queues/' + user, 'wb') as f:
                pickle.dump(queue, f)
            await ctx.message.channel.send("Added to your queue")
        if opt == 3:
            if len(args) < 3:
                await ctx.message.channel.send('Please enter the position you want to move from and to')
                return
            if len(args) > 3:
                await ctx.message.channel.send('Too much arguments so i only take the first two')
            try:
                pos1 = int(args[1])
                pos2 = int(args[2])
            except ValueError:
                await ctx.message.channel.send("Please enter a number")
            if 0 <= pos1 < len(queue) and pos2 <= len(queue):
                queue.insert(pos2, queue.pop(pos))
                with open('./cogs/queues/' + user, 'wb') as f:
                    pickle.dump(queue, f)
                await ctx.message.channel.send("Edited")
            else:
                await ctx.message.channel.send("Position out of range")
