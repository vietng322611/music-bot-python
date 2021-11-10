import os
import re
import requests
import asyncio
import json
import sys

from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL as youtubedl
from bs4 import BeautifulSoup as bs
from discord.ext import commands
from discord.utils import get
from logger import logger
from update import update
from dotenv import load_dotenv

config = json.load(open('./config.json'))
sys.stdout = logger(config)
if config["Check_Update_On_Start"] == "True":
    update(config)
sys.path.append(config["Directory"] + config["ffmpeg"].strip("."))
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
GUILD = os.getenv('GUILD')

bot = commands.Bot(command_prefix='!!')
queue = []
queue_info = []
banned_words_spam = {}
banned_words = ['lỏd'] # if you don't need you can delete it
creator = 853514227738214421
ydl_opts = {'format': 'bestaudio', 'noplaylist':'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

def get_video_info(url):
    r = requests.get(url)
    s = bs(r.text, "html.parser")
    title = s.find('title').get_text().replace(' - YouTube', '')
    return title

@bot.event
async def playing(ctx, voice):
    if queue != []:
        url = queue.pop(0)
        title = queue_info.pop(0)
        with youtubedl(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
        if not voice.is_playing():
            loop = asyncio.get_event_loop()
            voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda x=None: loop.create_task(playing(ctx, voice)))
            await ctx.send(f'**Now Playing:** `{title}`')
    return

@bot.event
async def get_message(ctx):
    try:
        parameter = await bot.wait_for("message", timeout=15)
        if parameter.author == bot.user:
            return None
        if parameter.content.startswith('!!'):
            return "cancel"
    except asyncio.TimeoutError:
        await ctx.channel.send("Sorry, you didn't reply in time!")
        return "cancel"
    try:
        if parameter.content == "cancel":
            return parameter.content
        else:
            return int(parameter.content)
    except:
        await ctx.message.channel.send('Please enter a number')
    return None

@bot.event
async def on_ready():
    print(f'Connected')

@bot.event
async def add_role(message):
    member = message.author
    role = get(message.guild.roles, name = "Mute")
    return await member.add_roles(role)

@bot.event
async def on_message(message):
    inp = message.content
    if message.author == bot.user:
        return
    if message.author.id != creator:
        for i in banned_words:
            if i in inp.lower():
                await message.delete()
                if message.author.id in banned_words_spam:
                    if banned_words_spam[message.author.id] > 4:
                        await add_role(message)
                        banned_words_spam[message.author.id] = 0
                        return await message.channel.send(f'<@{message.author.id}> banned because of spamming, using banned words many times', delete_after=5)
                    else:
                        banned_words_spam[message.author.id] += 1
                        return await message.channel.send(f"<@{message.author.id}> used banned word. Subsequent violations may be banned by creator.", delete_after=5)
                else:
                    banned_words_spam.update({message.author.id : 1})
                    return await message.channel.send(f"<@{message.author.id}> used banned word. Subsequent violations may be banned by creator.", delete_after=5)
    await bot.process_commands(message)
    return

@bot.command(name='leave', help='Leave voice channel')
async def leave(ctx):
    voice = ctx.message.guild.voice_client
    if voice != None:
        if voice.is_playing:
            voice.stop
        return await voice.disconnect()
    else:
        return await ctx.message.channel.send("I'm not in a voice channel now" )

@bot.command(name='play', help='Play music from url')
async def play(ctx):
    input = ctx.message.content
    if ctx.channel.id != 884739635543146510 and ctx.channel.id != 884706027818348545:  # this control where to send command message, you can change this
        return
    url = input.strip('!!play ')
    if not url.startswith("https://www.youtu") and not url.startswith("https://youtu") and not url.startswith("youtu"):
        await search(ctx)
        return
    queue.append(url)
    queue_info.append(get_video_info(url))
    status = ctx.author.voice
    if status == None:
        await ctx.message.channel.send('Please join a voice channel')
        return
    channel = status.channel
    voice = ctx.message.guild.voice_client
    try:
        await channel.connect()
    except Exception:
        if voice != channel:
            await voice.move_to(channel)
    voice =  ctx.message.guild.voice_client
    if not voice.is_playing():
        await playing(ctx, voice)
    else:
        await ctx.message.channel.send('Added to queue')
    return

@bot.command(name='stop', help='Stop player')
async def stop(ctx):
    if ctx.channel.id != 884739635543146510 and ctx.channel.id != 884706027818348545:
        return
    voice = ctx.message.guild.voice_client
    if voice == None:
        await ctx.channel.send("I wasn't in a voice channel")
        return
    voice.stop()
    await ctx.message.channel.send('Stopped')
    if queue == []:
        await voice.disconnect()
    else:
        await playing(ctx, voice)
    return

@bot.command(name='skip', help='Skip to next song in queue')
async def skip(ctx):
    if ctx.channel.id != 884739635543146510 and ctx.channel.id != 884706027818348545:
        return
    voice = ctx.message.guild.voice_client
    if queue != []:
        voice.stop()
        await playing(ctx, voice)
        return
    else:
        await ctx.message.channel.send('No song left')
    return

@bot.command(name='search', help='Search for a song on youtube and get first result add to queue')
async def search(ctx):
    input = ctx.message.content
    if ctx.channel.id != 884739635543146510 and ctx.channel.id != 884706027818348545:
        return
    req = input.strip('!!search ')
    r = requests.get("https://www.youtube.com/results?search_query=" + req)
    s = bs(r.text, "html.parser")
    ids = re.findall(r"watch\?v=(\S{11})", s.decode())
    urls = ''
    for i in range(5):
        urls += str(i) + ':' + get_video_info('https://www.youtube.com/watch?v=' + ids[i]) + '\n'
    await ctx.message.channel.send('`{}`'.format(urls))
    await ctx.message.channel.send('Please choose a song')
    parameter = None
    while parameter == None:
        parameter = await get_message(ctx)
    if parameter == "cancel":
        return await ctx.message.channel.send('Canceled')
    url = 'https://www.youtube.com/watch?v=' + ids[parameter]
    queue.append(url)
    queue_info.append(get_video_info(url))
    await ctx.message.channel.send('I added this to queue: {}'.format(url))
    voice =  ctx.message.guild.voice_client
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
    voice = ctx.message.guild.voice_client
    if not voice.is_playing():
        await playing(ctx, voice)
    return

@bot.command(name='delete', help='Delete a song from queue')
async def delete(ctx):
    input = ctx.message.content
    pos = input.strip('!!delete ')
    try:
        pos = int(pos)
    except:
        await ctx.message.channel.send('Please enter a number')
    try:
        queue.pop(pos)
        queue_info.pop(pos)
        await ctx.message.channel.send('Deleted from queue')
    except:
        await ctx.message.channel.send('Out of range')
    return
@bot.command(name='show-queue', help='Show current songs in queue')
async def show_queue(ctx):
    if len(queue) == 0:
        await ctx.message.channel.send('No song left')
        return
    count = 0
    list_queue = ''
    for i in queue_info:
        list_queue += f'{count}:{i}\n'
        count += 1
    return await ctx.message.channel.send(list_queue)

@bot.command(name='show-banned-words', help='Show a list of banned words')
async def show_banned_words(ctx):
    return await ctx.message.send(f'**Banned words :**{banned_words}')

bot.run(TOKEN)
