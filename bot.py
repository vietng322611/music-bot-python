# This made by vietng322611, please be respect, don't copy it without permission, you can change the code inside into your own.
# If something goes wrong, send me your log or try restarting the bot.

import modwall; modwall.check() # Library checker

import sys
import os
import json
import asyncio
import signal

from time import sleep
from discord.ext import commands
from discord.utils import get
from discord.embeds import Embed
from discord.colour import Color
from logger import logger
from update import update
from dotenv import load_dotenv
from cogs.music import music

config = json.load(open('./config.json'))
sys.stdout = logger(config)
if config["Check_Update_On_Start"] == "True":
    update(config)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = commands.Bot(description="A simple bot made by vietng322611", command_prefix=config["Prefix"])
bot.add_cog(music(bot))
queue = []
queue_info = []
banned_words_spam = {}
creator = 853514227738214421
banned_words = ['lỏd'] # if you don't need you can delete it

async def voice_check(voice):
    if voice != None:
        member_count = len(voice.channel.members)
        if member_count == 1:
            if voice.is_playing():
                voice.source.cleanup()       
                voice.stop()
            await voice.disconnect()

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

@bot.event
async def on_voice_state_update(member, before, after):
    if member.name == bot.user.name:
        return
    elif bot.voice_clients != []:
        voice = bot.voice_clients[0]
        if after.channel != voice:
            await voice_check(voice)

@bot.command(name='banned-words', help='Show a list of banned words')
async def show_banned_words(ctx):
    embed = Embed(color = Color.from_rgb(255, 0, 0))
    embed.add_field(name="Banned words", value=banned_words, inline=False)
    await ctx.message.send(embed=embed)

def clean(signum, frame):
    print("Logging bot out....")
    asyncio.get_event_loop().create_task(bot.close())
    print("Cleaning tasks....")
    [task.cancel() for task in asyncio.all_tasks()]
    asyncio.get_running_loop().stop()
    sys.exit()
    if RuntimeError:
        pass
    print("Good bye!")
    sleep(0.5)

signal.signal(signal.SIGINT, clean)
bot.run(TOKEN)