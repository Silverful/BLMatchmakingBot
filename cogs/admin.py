from discord.ext import commands
import discord
from settings import *


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def discord_info(self, ctx):
        guild = ctx.guild
        embed = discord.Embed()
        voice_channels = len(guild.voice_channels)
        text_channels = len(guild.text_channels)
        embed.add_field(name='Discord name', value=guild.name, inline=False)
        embed.add_field(name="# of voice channels", value=str(voice_channels))
        embed.add_field(name="# of text channels", value=str(text_channels))
        await ctx.send(embed=embed)


def setup(bot):
    print('Matchmaking Bot is online!')
#   it is a first cog to load
    bot.add_cog(Admin(bot))
