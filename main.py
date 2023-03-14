# This made by vietng322611, please be respect, don't copy it without permission, you can change the code inside into your own.
# If something goes wrong, DM me your log or try restarting the bot.

import modwall; modwall.check() # Library checker

import asyncio
import sys
import os
import json
import discord

from discord.ext import commands
from discord.utils import get
from logger import logger
from update import update
from dotenv import load_dotenv
from cogs.music import music
from cogs.extent import extent
from gtts import gTTS
from time import sleep

config = json.load(open('./config.json'))
if not os.path.exists('logs'):
    os.mkdir('logs')
sys.stdout = logger(config)

if config["Check_Update_On_Start"] == "True":
    update(config)

load_dotenv('token.env')
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True
intents.messages = True
bot = commands.Bot(description="I'm a happy bot", command_prefix=config["Prefix"], intents=intents)
queue = []
queue_info = []
creator = config["Creator_Id"]

async def voice_check(voice, channel): # Check if only bot in voice channel
    member_count = len(channel.members)
    if member_count == 1:
        if voice.is_playing():
            voice.source.cleanup()       
            voice.stop()
        await voice.disconnect()
    return

@bot.event
async def on_ready():
    print(f'Connected')

@bot.event
async def on_voice_state_update(member, before, after): # Get voice status
    if member.name == bot.user.name:
        return
    elif bot.voice_clients != []:
        voice = get(bot.voice_clients, guild=member.guild)
        channel = bot.get_channel(voice.channel.id)
        if after.channel == None or after.channel != channel: 
            if before.channel.id == channel.id:
                await voice_check(voice, channel)
                return
        else:
          if before.channel == None and after.channel.id == channel.id: # If someone joins the voice channel of the bot, bot will say something, j4f
            if not voice.is_playing():
              tts = gTTS(text=config["Voice_Greetting"], lang=config["gg_Command_lang"])
              tts.save('gg.mp3')
              sleep(1.5)
              voice.play(discord.FFmpegPCMAudio('gg.mp3'))
              voice.source = discord.PCMVolumeTransformer(voice.source, volume=2.0)
              return
            
@bot.event
async def on_member_join(member): #testing
    server = bot.get_server(member.server)
    print(member)
    await get(server.text_channels, name='welcome').send(f"{member.name} has joined")

@bot.event
async def on_member_remove(member): #testing
    server = bot.get_server(member.server)
    print(member)
    await get(server.text_channels, name='welcome').send(f"{member.name} has leaved")

async def main():
    async with bot:
        await bot.add_cog(music(bot, config))
        await bot.add_cog(extent(bot, config))
        await bot.start(TOKEN)

asyncio.run(main())