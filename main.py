# This made by vietng322611, please be respect, don't copy it without permission, you can change the code inside into your own.
# If something goes wrong, DM me (murasaki#1843) your log or try restarting the bot.

''' TODO:
    + Make a spammer detector
    + Clean app after exit
    + Rebuild logger.py
 '''
# ! Fix certains bugs cause app to crash

import modwall; modwall.check() # Library checker

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

# Check config file directory
config = json.load(open('./config.json'))
if not os.path.exists('logs'):
    os.mkdir('logs')
sys.stdout = logger(config)

if config["Check_Update_On_Start"] == "True":
    update(config)

load_dotenv('token.env')
TOKEN = os.getenv("BOT_TOKEN")

bot = commands.Bot(description="", command_prefix=config["Prefix"]) 
bot.add_cog(music(bot, config))
bot.add_cog(extent(bot, config))
queue = [] # Music queue
queue_info = [] # Music info
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
async def add_role(message): # Add mute role to user if they are spamming banned words
    member = message.author
    role = get(message.guild.roles, name = "Mute")
    return await member.add_roles(role)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

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
          if before.channel == None and after.channel.id == channel.id: # If someone joins the voice channel of the bot, bot will say somgthing, j4f
            if not voice.is_playing():
              tts = gTTS(text=config["Voice_Greetting"].format(member.name), lang=config["gg_Command_lang"])
              tts.save('gg.mp3')
              sleep(1.5)
              voice.play(discord.FFmpegPCMAudio('gg.mp3'))
              voice.source = discord.PCMVolumeTransformer(voice.source, volume=2.0)
              return

bot.run(TOKEN)