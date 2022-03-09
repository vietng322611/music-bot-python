from discord.embeds import Embed
from discord.colour import Color
from discord.ext import commands

class extent(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    @commands.command(name="avatar", help="Get a user avatar")
    async def avatar(self, ctx):
        if ctx.message.mentions:
            for i in ctx.message.mentions:
                embed = Embed(title=f"{i.name}'s avatar", color=Color.red())
                embed.set_image(url=i.avatar_url)
                await ctx.send(embed=embed)
        else:
            embed = Embed(title=f"{ctx.message.author.name}'s avatar", color=Color.red())
            embed.set_image(url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)