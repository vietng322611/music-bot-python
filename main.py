# This made by vietng322611, please be respect, don't copy it without permission, you can change the code inside into your own.
# If something goes wrong, DM me your log or try restarting the bot.

import modwall; modwall.check() # Library checker

import sys
import os
import json
import discord

from collections import defaultdict
from discord.ext import commands
from discord.utils import get
from discord.embeds import Embed
from discord.colour import Color
from logger import logger
from update import update
from dotenv import load_dotenv
from cogs.music import music
from cogs.extent import extent
from gtts import gTTS
from time import sleep
from datetime import datetime, timedelta

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
bot = commands.Bot(description="I'm a happy bot", command_prefix=config["Prefix"], intents=intents)
bot.add_cog(music(bot, config))
bot.add_cog(extent(bot, config))
queue = []
queue_info = []
banned_words_spam = defaultdict(int)
creator = config["Creator_Id"]
banned_words = config["Banned_Words"]

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
    inp = message.content
    if message.author == bot.user:
        return
    if message.author.id != creator:
        for i in banned_words:
            if i + " " in inp.lower() or inp.lower() == i:
                await message.delete()
                if banned_words_spam[message.author.id] > 4:
                    await message.author.timeout(datetime.now() + timedelta(minutes = 5))
                    await message.channel.send(f"<@{message.author.id}> timed out user for 5 minutes for spamming banned word.", delete_after=5)
                    banned_words_spam[message.author.id] = 0
                    return

                else:
                    banned_words_spam[message.author.id] += 1
                    return await message.channel.send(f"<@{message.author.id}> used banned word. Subsequent violations may be banned by creator.", delete_after=5)
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

@bot.command(name='banned-words', help='Show a list of banned words')
async def show_banned_words(ctx):
  embed = Embed(color = Color.from_rgb(255, 0, 0))
  embed.add_field(name="Banned words", value=banned_words, inline=False)
  await ctx.message.channel.send(embed=embed)

bot.run(TOKEN)