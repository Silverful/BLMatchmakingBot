from discord.ext import commands
from discord_components import *
from settings import *
import discord
import random
from matchmaking import sheets, match, mmdiscord


class Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(founder_role_name)
    async def button(self, ctx):
        await mmdiscord.send_button(ctx, self.bot, True, False)

    @commands.command()
    @commands.has_role(founder_role_name)
    async def asdf(self, ctx):
        embed = discord.Embed(title='```json\n"---------------------     asdf     ---------------------"\n```',
                              description='**fdsa**')
        await ctx.send(embed=embed)


async def send_button(ctx, bot, correct_request, no_free_channels=False):
    start_button = Button(label='Start!', style=4, custom_id='start_button')
    if correct_request:
        await ctx.send('Good luck!', components=[start_button])

    button_interaction = await bot.wait_for('button_click', check=lambda x: x.custom_id == 'start_button')

    correct_request = True
    if not button_interaction.user.voice:
        correct_request = False
        await ctx.send("You're not in a voice channel", delete_after=5)
    elif not button_interaction.user.voice.channel.name == team_building_voice_channel_name:
        correct_request = False
        await ctx.send("You're in a wrong voice channel", delete_after=5)
    elif not len(button_interaction.user.voice.channel.members) >= 12:
        correct_request = False
        await ctx.send('Not enough players, need %s more' %
                       str(12 - (len(button_interaction.user.voice.channel.members))), delete_after=5)

    if no_free_channels:
        correct_request = False

    if not correct_request:
        await send_button(ctx, bot, False, False)
        return
    if correct_request:
        await button_interaction.message.delete()
        voice_members = button_interaction.user.voice.channel.members

        removed_members = []
        while (len(voice_members) % 12) != 0:
            removed_member = random.choice(voice_members)
            voice_members.remove(removed_member)
            removed_members.append(removed_member)

        await ctx.send(random.choice(waiting_phrases), delete_after=5)

        player_data = sheets.find_players(voice_members)
        players = player_data[0]
        for not_found_member in player_data[1]:
            sheets.add_player(not_found_member)

        await ctx.send(random.choice(waiting_phrases), delete_after=10)

        players.sort(key=lambda x: x.mmr, reverse=True)

        team1_voice_channel = discord.utils.find(lambda x: x.name == team1_voice_channel_name,
                                                 ctx.channel.category.channels)
        team3_voice_channel = discord.utils.find(lambda x: x.name == team3_voice_channel_name,
                                                 ctx.channel.category.channels)
        team5_voice_channel = discord.utils.find(lambda x: x.name == team5_voice_channel_name,
                                                 ctx.channel.category.channels)
        team7_voice_channel = discord.utils.find(lambda x: x.name == team7_voice_channel_name,
                                                 ctx.channel.category.channels)

        while len(players) > 0:
            game_players = []
            while len(game_players) != 12:
                game_players.append(players[0])
                players.pop(0)

            game = match.Match(game_players)
            game.set_roles()
            game.make_teams()

            team1_players = []
            team2_players = []

            for match_player in game.team1:
                team1_players.append(ctx.guild.get_member(int(match_player.discord_id)))
            for match_player in game.team2:
                team2_players.append(ctx.guild.get_member(int(match_player.discord_id)))

            if not team1_voice_channel.members:
                team2_voice_channel = discord.utils.find(lambda x: x.name == team2_voice_channel_name,
                                                         ctx.channel.category.channels)
                team1_founded_voice_channel = team1_voice_channel
                team2_founded_voice_channel = team2_voice_channel
            elif not team3_voice_channel.members:
                team4_voice_channel = discord.utils.find(lambda x: x.name == team4_voice_channel_name,
                                                         ctx.channel.category.channels)
                team1_founded_voice_channel = team3_voice_channel
                team2_founded_voice_channel = team4_voice_channel
            elif not team5_voice_channel.members:
                team6_voice_channel = discord.utils.find(lambda x: x.name == team6_voice_channel_name,
                                                         ctx.channel.category.channels)
                team1_founded_voice_channel = team5_voice_channel
                team2_founded_voice_channel = team6_voice_channel
            elif not team7_voice_channel.members:
                team8_voice_channel = discord.utils.find(lambda x: x.name == team8_voice_channel_name,
                                                         ctx.channel.category.channels)
                team1_founded_voice_channel = team7_voice_channel
                team2_founded_voice_channel = team8_voice_channel
            else:
                await ctx.send('No free voice channels found', delete_after=10)
                await send_button(ctx, bot, True, True)
                return

            for member in team1_players:
                await member.move_to(team1_founded_voice_channel)
            #                    await asyncio.sleep(0.3)

            await ctx.send('Moving players...', delete_after=20)

            for member in team2_players:
                await member.move_to(team2_founded_voice_channel)
            #                    await asyncio.sleep(0.3)

            if sort_teams_by == 'MMR':
                game.sort_teams_by_mmr()

            embed = mmdiscord.form_teams_embed(game.team1, game.team2)
            await ctx.send(embed=embed)

    await send_button(ctx, bot, True, False)


def setup(bot):
    bot.add_cog(Basic(bot))
