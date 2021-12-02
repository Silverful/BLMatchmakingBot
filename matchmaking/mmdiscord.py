import discord.utils
from settings import *
from discord_components import Button
import discord
import random
from matchmaking import sheets, match
from discord.ext import commands


def form_teams_embed(team1, team2):

    team1_avg_mmr = 0
    team2_avg_mmr = 0

    factions = [
        'Khuzait',
        'Empire',
        'Sarranids',
        'Sturgia',
        'Vlandia',
        'Battania'
    ]
    skirmish_maps = [
        'Echerion',
        'Trading post',
        'Xauna',
        'Town outskirts',
        'Port Omor'
    ]
    class_fix = {
        'cav': 'Cavalry',
        'arch': 'Archer',
        'inf': 'Infantry'
    }

    for player1 in team1:
        team1_avg_mmr += player1.mmr
    for player2 in team2:
        team2_avg_mmr += player2.mmr
    team1_avg_mmr //= 6
    team2_avg_mmr //= 6
    team1_cap_no = random.randrange(0, 6)
    team2_cap_no = random.randrange(0, 6)

    embed = discord.Embed(title='Bannerlord matchmaking teams', description='Map: %s' % random.choice(skirmish_maps))

    embed.add_field(name=('%s - Team %s' % (random.choice(factions), team1[team1_cap_no].nickname)),
                    value=('Average MMR = ' + str(team1_avg_mmr)), inline=False)
    for player1 in team1:
        embed.add_field(name=player1.nickname, value=(class_fix[player1.main] + '\n' + str(player1.mmr)), inline=True)

    embed.add_field(name=('%s - Team %s' % (random.choice(factions), team2[team2_cap_no].nickname)),
                    value=('Average MMR = ' + str(team2_avg_mmr)), inline=False)
    for player2 in team2:
        embed.add_field(name=player2.nickname, value=(class_fix[player2.main] + '\n' + str(player2.mmr)), inline=True)

    embed.add_field(name='Teams average MMR difference', value=str(abs(team1_avg_mmr - team2_avg_mmr)))

    return embed


def form_player_embed(member):

    class_fix = {
        'cav': 'Cavalry',
        'arch': 'Archer',
        'inf': 'Infantry'
    }

    class_color = {
        'cav': discord.colour.Color.dark_red(),
        'arch': discord.colour.Color.orange(),
        'inf': discord.colour.Color.dark_green()
    }

    desc_stats = 'Current rating position: %s\n' % member.top + \
                 'MMR: %s\n' % member.mmr + \
                 'Total games: %s\n' % member.matches + \
                 'Win rate: %s\n' % member.winrate + \
                 'MVP rate: %s\n' % member.mvp_rate

    embed = discord.Embed(title='---------------------     %s     ---------------------' % member.nickname,
                          description=desc_stats, color=class_color[member.main])
    embed.add_field(name='Clan', value=member.clan, inline=True)
    embed.add_field(name='Main class', value=class_fix[member.main], inline=True)
    embed.add_field(name='Secondary class', value=class_fix[member.secondary], inline=True)
    embed.add_field(name='Total kills', value=member.kills, inline=True)
    embed.add_field(name='Total assists', value=member.assists, inline=True)
    embed.add_field(name='Total score', value=member.score, inline=True)
    embed.add_field(name='Kills per round', value=member.kr, inline=True)
    embed.add_field(name='Assists per round', value=member.ar, inline=True)
    embed.add_field(name='Score per round', value=member.sr, inline=True)

    return embed


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
        users = voice_members
        players = []
        player_count = 0

        for mm_player in users:
            player_count += 1
            player_to_add = sheets.find_player(mm_player)

            if player_count % 10 == 0:
                await ctx.send(random.choice(waiting_phrases), delete_after=5)

            if player_to_add:
                players.append(player_to_add)

            else:
                sheets.add_player(mm_player)
                players.append(sheets.find_player(mm_player))

        await ctx.send(random.choice(waiting_phrases), delete_after=10)

        players.sort(key=lambda x: x.mmr, reverse=True)

        team1_voice_channel = discord.utils.find(lambda x: x.name == team1_voice_channel_name,
                                                 ctx.category.channels)
        team3_voice_channel = discord.utils.find(lambda x: x.name == team3_voice_channel_name,
                                                 ctx.category.channels)
        team5_voice_channel = discord.utils.find(lambda x: x.name == team5_voice_channel_name,
                                                 ctx.category.channels)
        team7_voice_channel = discord.utils.find(lambda x: x.name == team7_voice_channel_name,
                                                 ctx.category.channels)

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
                                                         ctx.category.channels)
                team1_founded_voice_channel = team1_voice_channel
                team2_founded_voice_channel = team2_voice_channel
            elif not team3_voice_channel.members:
                team4_voice_channel = discord.utils.find(lambda x: x.name == team4_voice_channel_name,
                                                         ctx.category.channels)
                team1_founded_voice_channel = team3_voice_channel
                team2_founded_voice_channel = team4_voice_channel
            elif not team5_voice_channel.members:
                team6_voice_channel = discord.utils.find(lambda x: x.name == team6_voice_channel_name,
                                                         ctx.category.channels)
                team1_founded_voice_channel = team5_voice_channel
                team2_founded_voice_channel = team6_voice_channel
            elif not team7_voice_channel.members:
                team8_voice_channel = discord.utils.find(lambda x: x.name == team8_voice_channel_name,
                                                         ctx.category.channels)
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

            embed = form_teams_embed(game.team1, game.team2)
            await ctx.send(embed=embed)

    await send_button(ctx, bot, True, False)


async def fetch_button(bot):
    matchmaking_guild = bot.get_guild(id=hinq_guild_id)
    teammaker_channel = discord.utils.find(lambda x: x.name == team_building_text_channel_name,
                                           matchmaking_guild.channels)
    messages = await teammaker_channel.history(limit=10).flatten()
    for message in messages:
        if message.content == 'Good luck!':
            await message.delete()

    await send_button(teammaker_channel, bot, True, False)


def founder():
    def predicate(ctx):
        return commands.check_any(
            commands.has_role(founder_role_name),
            commands.is_owner()
        )
    return commands.check(predicate)


def admin():
    def predicate(ctx):
        return commands.check_any(
            commands.has_role(founder_role_name),
            commands.has_role(admin_role_name),
            commands.is_owner()
        )
    return commands.check(predicate)


def moder():
    def predicate(ctx):
        return commands.check_any(
            commands.has_role(founder_role_name),
            commands.has_role(admin_role_name),
            commands.has_role(moderator_role_name),
            commands.is_owner()
        )
    return commands.check(predicate)


def member():
    def predicate(ctx):
        return commands.check_any(
            commands.has_role(founder_role_name),
            commands.has_role(admin_role_name),
            commands.has_role(moderator_role_name),
            commands.has_role(player_role_name),
            commands.is_owner()
        )
    return commands.check(predicate)
