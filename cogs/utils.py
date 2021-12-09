from discord.ext import commands
import discord.utils
from settings import *
from matchmaking import player, match, mmdiscord
import asyncio


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(moderator_role_name)
    async def embed_test(self, ctx):
        print(str(ctx.message.author), ': ', str(ctx.message.content))

        playerlist = player.form_random_players()
        game = match.Match(playerlist)

        game.set_roles()
        game.make_teams()
        if sort_teams_by == 'MMR':
            game.sort_teams_by_mmr()

        embed = mmdiscord.form_teams_embed(game.team1, game.team2)
        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_role(moderator_role_name)
    async def voice_id(self, ctx):
        print(str(ctx.message.author), ': ', str(ctx.message.content))
        if ctx.author.voice:
            await ctx.send('Voice channel ID: ' + str(ctx.author.voice.channel.id))
        else:
            await ctx.send('You''re not in a voice channel')

    @commands.command(brief='IDs of all users ')
    @commands.is_owner()
    async def user_ids(self, ctx):
        print(str(ctx.message.author), ': ', str(ctx.message.content))
        for member in ctx.guild.members:
            await ctx.send(member.name.ljust(20) + str(member.id))

    @commands.command(brief='Finds a player by ID')
    @commands.has_role(moderator_role_name)
    async def find(self, ctx, user_id=0):
        print(str(ctx.message.author), ': ', str(ctx.message.content))
        if user_id == 0:
            user_id = ctx.author.id
        user = await self.bot.fetch_user(user_id)
        await ctx.send(user.name)

    @commands.command(name='text_id')
    @commands.has_role(moderator_role_name)
    async def text_id(self, ctx):
        print(str(ctx.message.author), ': ', str(ctx.message.content))
        await ctx.send('Text channel ID: ' + str(ctx.channel.id))

    @commands.command()
    @commands.has_role(moderator_role_name)
    async def split(self, ctx):
        print(str(ctx.message.author), ': ', str(ctx.message.content))
        channel = ctx.message.author.voice.channel
        a = 0
        for member in channel.members:
            if a % 2 == 1:
                channel = discord.utils.find(lambda x: x.name == team1_voice_channel_name,
                                             ctx.channel.category.channels)
                await member.move_to(channel)
#                await asyncio.sleep(0.3)
            else:
                channel = discord.utils.find(lambda x: x.name == team2_voice_channel_name,
                                             ctx.channel.category.channels)
                await member.move_to(channel)
#                await asyncio.sleep(0.3)
            a += 1


def setup(bot):
    bot.add_cog(Utils(bot))
