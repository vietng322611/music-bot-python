# This made by vietng322611, please be respect, don't copy it without permission, you can change the code inside into your own.
# If something goes wrong, send me your log or try restarting the bot.

import sys
import asyncio
import os
import json

from discord.ext import commands
from discord.utils import get
from logger import logger
from update import update
from dotenv import load_dotenv
from music import music

config = json.load(open('./config.json'))
sys.stdout = logger(config)
if config["Check_Update_On_Start"] == "True":
    update(config)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GUILD = os.getenv("SERVER_NAME")

bot = commands.Bot(description="A simple bot made by vietng322611", command_prefix='!!')
bot.add_cog(music(bot))
queue = []
queue_info = []
banned_words_spam = {}
creator = 853514227738214421
banned_words = ['lỏd'] # if you don't need you can delete it

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

@bot.command(name='vol', help='Change bot volume')
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
    if input.isnumeric() == False:
        await ctx.message.channel.send('Please enter a number from 0 to 200')
        return
    input = float(input)
    if input < 0 or input > 200:
        await ctx.message.channel.send('Please enter a number from 0 to 200')
        return
    volume = input / 100
    voice.source.volume = volume
    return await ctx.message.channel.send(f'**Volume changed to** {input}/200')

@bot.command(name='leave', help='Leave voice channel')
async def leave(ctx):
    voice = ctx.voice_client
    if voice != None:
        if voice.is_playing:
            voice.stop()
        return await voice.disconnect()
    else:
        return await ctx.message.channel.send("I'm not in a voice channel now" )

@bot.command(name='stop', help='Stop bot playing songs')
async def stop(ctx):
    voice = ctx.voice_client 
    if voice == None:
        await ctx.channel.send("I'm not playing anything")
        return 
    if queue == []:
        voice.stop()
        await voice.disconnect()
    else:
        voice.stop()
    await ctx.message.channel.send('Stopped')
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
