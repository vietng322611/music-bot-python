# This made by vietng322611, please be respect, don't copy it without permission, you can change the code inside into your own.
# If something goes wrong, DM me your log or try restarting the bot.

import modwall; modwall.check() # Library checker

import sys
import os
import json
import discord

from discord.ext import commands
from discord.utils import get
from discord.embeds import Embed
from discord.colour import Color
from logger import logger
from update import update
from dotenv import load_dotenv
from cogs.music import music
from gtts import gTTS
from time import sleep

config = json.load(open('./config.json'))
if not os.path.exists('logs'):
    os.mkdir('logs')

sys.stdout = logger(config)
sys.stderr.write = logger(config)

if config["Check_Update_On_Start"] == "True":
    update(config)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(description="A simple bot made by vietng322611", command_prefix=config["Prefix"], intents=intents)
bot = commands.Bot(description="A simple bot made by vietng322611", command_prefix=config["Prefix"])
bot.add_cog(music(bot))
queue = []
queue_info = []
banned_words_spam = {}
creator = config["Creator_Id"]
banned_words = ['lỏd', 'emotional damage', 'ì mâu sần nồ đam mẹt', 'ì mâu sần nồ đam mệt', 'emotional dâmge', 'sang chấn tâm lí', 'sang chấn tâm lý']

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
            if i in inp.lower():
                await message.delete()
                if message.author.id in banned_words_spam: # Check if user is using banned words
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
async def on_voice_state_update(member, before, after): # Get voice status
    if member.name == bot.user.name:
        return
    elif bot.voice_clients != []:
        voice = get(bot.voice_clients, guild=member.guild)
        channel = bot.get_channel(voice.channel.id)
        if after.channel == None: 
            if before.channel.id == channel.id:
                await voice_check(voice, channel)
                return
        else:
          if after.channel.id == channel.id: # If someone joins the voice channel of the bot, bot will say somgthing, j4f
            if not voice.is_playing():
              tts = gTTS(text="Ây thằng nhóc vừa vào mà không chào ai à", lang='vi')
              tts.save('gg.mp3')
              sleep(1)
              voice.play(discord.FFmpegPCMAudio('gg.mp3'))
              voice.source = discord.PCMVolumeTransformer(voice.source, volume=2.0)
              return
@bot.event
async def on_member_join(member):
  server = bot.get_server(member.server)
  print(server)
  await get(server.text_channels, name='welcome').send(f"{member.name} has joined")

@bot.event
async def on_member_remove(member):
  server = bot.get_server(member.server)
  print(server)
  await get(server.text_channels, name='welcome').send(f"{member.name} has leaved")

@bot.command(name='banned-words', help='Show a list of banned words')
async def show_banned_words(ctx):
  embed = Embed(color = Color.from_rgb(255, 0, 0))
  embed.add_field(name="Banned words", value=banned_words, inline=False)
  await ctx.message.channel.send(embed=embed)

bot.run(TOKEN)
