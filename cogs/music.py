from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.embeds import Embed
from discord.colour import Color
from discord.ext import commands
from cogs.UrlHandler import url_exec

import asyncio

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 3','options': '-vn'}
        self.queue = []
        self.titles = []
        self.users = []
        self.thumbnails = []
        self.avatar_urls = []
        self.current_song = ""

    def add_to_queue(self, url, url2, title, user, thumbnail, avatar_url):
        self.queue.append(url2)
        self.titles.append(title)
        self.titles.append(url)
        self.thumbnails.append(thumbnail)
        self.users.append(user)
        self.avatar_urls.append(avatar_url)

    async def playing(self, ctx, voice):
        embed = Embed(color = Color.from_rgb(255, 0, 0))
        if not voice.is_playing():
            if self.queue != []:
                player = self.queue.pop(0)
                title = self.titles.pop(0)
                url = self.titles.pop(0)
                thumbnail = self.thumbnails.pop(0)
                self.current_song = title
                user = self.users.pop(0)
                avatar = self.avatar_urls.pop(0)
                loop = asyncio.get_event_loop()
                embed.set_thumbnail(url=thumbnail)
                embed.add_field(name="Now Playing", value=f"[{title}]({url})", inline=False)
                embed.set_footer(text=f"Requested by {user}", icon_url=avatar)
                voice.play(FFmpegPCMAudio(player, **self.FFMPEG_OPTS), after=lambda x=None: loop.create_task(self.playing(ctx, voice)))
                voice.source = PCMVolumeTransformer(voice.source, volume=1.0)
                await ctx.send(embed=embed)
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
        url = input.strip('!!play ')
        if not url.startswith("https://www.youtu") and not url.startswith("https://youtu") and not url.startswith("youtu"):
            url = 'https://www.youtube.com/watch?v=' + url_exec.request(url)[0]
        url2, title = url_exec.ytdl(url)
        thumbnail_url = url_exec.get_thumbnail(url)
        self.add_to_queue(url, url2, title, ctx.author.name, thumbnail_url, ctx.author.avatar_url)
        channel = status.channel
        if voice != None:
            if voice != channel:
                await voice.move_to(channel)
        else:
            await channel.connect()
        voice = ctx.voice_client
        if not voice.is_playing():
            await self.playing(ctx, voice)
        else:
            embed = Embed(color=Color.from_rgb(255, 0, 0))
            embed.set_thumbnail(url=thumbnail_url)
            embed.add_field(name="Added to queue", value=f"[{title}]({url})", inline=False)
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.message.channel.send(embed=embed)
        return
    
    @commands.command(name='stop', aliases=['s'],help='Stop bot playing songs')
    async def stop(self, ctx):
        voice = ctx.voice_client 
        if voice == None:
            await ctx.channel.send("I'm not playing anything")
            return 
        else:
            voice.stop()
            await voice.disconnect()
        return await ctx.message.channel.send('Stopped')

    @commands.command(name='search', help='Search for a song on youtube', usage='[name]')
    async def search(self, ctx):
        input = ctx.message.content
        input = input.strip('!!search ')
        res = url_exec.request(input)
        urls = ''
        for i in range(5):
            urls += str(i) + ':' + url_exec.get_video_info('https://www.youtube.com/watch?v=' + res[i]) + '\n'
        embed = Embed(color = Color.from_rgb(255, 0, 0))
        embed.add_field(name=f'Result for "{input}"', value=urls, inline=False)
        await ctx.message.channel.send(embed=embed)
        await ctx.message.channel.send('Please choose a song')
        parameter = None
        while parameter == None:
            parameter = await self.get_message(ctx, ctx.message.author)
        if parameter == "cancel":
            return await ctx.message.channel.send('Canceled')
        url = 'https://www.youtube.com/watch?v=' + res[parameter]
        url2, title = url_exec.ytdl(url)
        thumbnail_url = url_exec.get_thumbnail(url)
        self.add_to_queue(url, url2, title, ctx.author.name, thumbnail_url, ctx.author.avatar_url)
        embed = Embed(color = Color.from_rgb(255, 0, 0))
        embed.set_thumbnail(url=thumbnail_url)
        embed.add_field(name="Added", value=f"[{title}]({url})", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        await ctx.message.channel.send(embed=embed)
        voice = ctx.guild.voice_client 
        if voice == None:
            status = ctx.author.voice
            if status == None:
                return
            channel = status.channel
            if voice == None:
                await channel.connect()
            else:
                if voice != channel:
                    await voice.move_to(channel)
        voice = ctx.voice_client
        if not voice.is_playing():
            await self.playing(ctx, voice)
        return
    
    @commands.command(name='skip', help='Skip to next song in queue')
    async def skip(self, ctx):
        voice = ctx.guild.voice_client
        if voice == None:
            await ctx.message.channel.send("I'm not playing anything")
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
            await ctx.message.channel.send('Deleted from queue')
        except:
            await ctx.message.channel.send('Out of range')
        return

    @commands.command(name='queue', help='Show current songs in queue')
    async def show_queue(self, ctx):
        embed = Embed(color = Color.from_rgb(255, 0, 0))
        embed.add_field(name="Currently Playing", value=self.current_song, inline=False)
        if len(self.queue) == 0:
            voice = ctx.voice_client
            if voice.is_playing:
                await ctx.message.channel.send(embed=embed)
            elif voice == None:
                await ctx.message.channel.send('No song left')
            return
        count = 0
        list_queue = ''
        for i in self.titles:
            list_queue += f'{count}: {i}\n'
            count += 1
        embed.add_field(name="Queued songs", value=list_queue, inline=False)
        return await ctx.message.channel.send(embed=embed)