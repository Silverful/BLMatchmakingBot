from matchmaking import sheets, match, mmdiscord
from discord.ext import commands
import discord.utils
from settings import *
import random
import asyncio
from country_list import countries_for_language
from matchmaking.mmdiscord import founder, admin, moder, member


class Matchmaking(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.mm_starts = False

    @commands.command(name='class', brief='Changes your classes. Use !mm class main_class secondary_class')
    @member()
    async def classes(self, ctx, main=None, secondary=None, player=None):
        if (not main) or (not secondary):
            await ctx.send('Please add both main and secondary classes ', delete_after=5)
            await ctx.message.delete()
            return

        if not (main in role_fix_names):
            await ctx.send('No such class %s found' % main, delete_after=5)
            await ctx.message.delete()
            return

        if not (secondary in role_fix_names):
            await ctx.send('No such class %s found' % secondary, delete_after=5)
            await ctx.message.delete()
            return

        if sheets.role_fix_names(main) == sheets.role_fix_names(secondary):
            await ctx.send('Main and secondary classes should be different', delete_after=5)
            await ctx.message.delete()
            return

        if player:
            admin_role = discord.utils.find(lambda x: x.name == sheet_edit_perms, ctx.message.guild.roles)
            if admin_role in ctx.author.roles:

                member = discord.utils.find(lambda x: x.display_name.lstrip(' ◦◊❃⌇୭૬৸৶৯ৡঙঐ') == player,
                                            ctx.guild.members)

                if not member:
                    await ctx.send('No such discord user %s found' % player, delete_after=5)
                    await ctx.message.delete()
                    return

            else:
                await ctx.send('No permissions', delete_after=5)
                await ctx.message.delete()
                return
        else:
            member = ctx.author

        found_player = sheets.find_player(member)
        if not found_player:
            await ctx.send('No player %s found' % member.display_name.lstrip(' ◦◊❃⌇୭૬৸৶৯ৡঙঐ'), delete_after=5)
            await ctx.message.delete()
            return

        sheets.change_classes(member, main, secondary)
        await ctx.send('Classes of player %s have been changed to Main: %s and Secondary: %s' %
                       (member.name, sheets.role_fix_names(main), sheets.role_fix_names(secondary)),
                       delete_after=10)

        await ctx.message.delete()

    @commands.command(brief='Changes your clan. Use !mm clan clan_name')
    @admin()
    async def clan(self, ctx, clan, player=None):
        if player:
            admin_role = discord.utils.find(lambda x: x.name == sheet_edit_perms, ctx.message.guild.roles)
            if admin_role in ctx.author.roles:

                member = discord.utils.find(lambda x: x.display_name.lstrip(' ◦◊❃⌇୭૬৸৶৯ৡঙঐ') == player,
                                            ctx.guild.members)

                if not member:
                    await ctx.send('No such discord user %s found' % player, delete_after=5)
                    await ctx.message.delete()
                    return

            else:
                await ctx.send('No permissions', delete_after=5)
                await ctx.message.delete()
                return
        else:
            member = ctx.author

        found_player = sheets.find_player(member)
        if not found_player:
            await ctx.send('No player %s found' % member.display_name.lstrip(' ◦◊❃⌇୭૬৸৶৯ৡঙঐ'), delete_after=5)
            await ctx.message.delete()
            return

        if clan in clan_list or clan in no_clan:
            sheets.change_clan(member, clan)
            await ctx.send('Changed the clan of player %s to %s' % (member.name, clan), delete_after=10)
        else:
            await ctx.send(('No clan %s in the clan list. \nCurrent clan list = ' % clan) + str(clan_list) +
                           '. \nContact Matchmaking admininstration to register a new clan', delete_after=10)

        await ctx.message.delete()

    @commands.command()
    @admin()
    async def country(self, ctx, country, player=None):
        if player:
            admin_role = discord.utils.find(lambda x: x.name == sheet_edit_perms, ctx.message.guild.roles)
            if admin_role in ctx.author.roles:

                member = discord.utils.find(lambda x: x.display_name.lstrip(' ◦◊❃⌇୭૬৸৶৯ৡঙঐ') == player,
                                            ctx.guild.members)

                if not member:
                    await ctx.send('No such discord user %s found' % player, delete_after=5)
                    await ctx.message.delete()
                    return

            else:
                await ctx.send('No permissions', delete_after=5)
                await ctx.message.delete()
                return
        else:
            member = ctx.author

        found_player = sheets.find_player(member)
        if not found_player:
            await ctx.send('No player %s found' % member.display_name.lstrip(' ◦◊❃⌇୭૬৸৶৯ৡঙঐ'), delete_after=5)
            await ctx.message.delete()
            return

        country_dict = dict(countries_for_language('en'))

        if (not (country in country_dict.values())) and (not (country in country_dict.keys())):
            await ctx.send('No country %s found in country list' % country, delete_after=5)
            await ctx.message.delete()
            return

        if country in country_dict.keys():
            country = country_dict[country]

        sheets.change_country(member, country)
        await ctx.send('Country of player %s changed to %s' % (member.name, country), delete_after=20)
        await ctx.message.delete()

    @commands.command(brief='Use !mm info for your own stats or !mm info [player1] [player2]')
    @member()
    async def info(self, ctx, *args):
        print(str(ctx.message.author), ': ', str(ctx.message.content))
        author = ctx.message.author
        if len(args) == 0:
            args = [author.display_name.lstrip(' ◦◊❃⌇୭૬৸৶৯ৡঙঐ')]
        if len(args) == 1 and args[0] == 'voice':
            if ctx.author.voice:
                member_list = []
                not_found_players_list = []

                for member in ctx.author.voice.channel.members:
                    found_player = sheets.find_player(member)
                    if found_player:
                        member_list.append(found_player)
                    else:
                        not_found_players_list.append(member)

                member_list.sort(key=lambda x: x.mmr, reverse=True)

                for member in member_list:
                    embed = mmdiscord.form_player_embed(member)
                    await ctx.send(embed=embed, delete_after=600)

                not_found_players_message = 'Players '
                if not_found_players_list:
                    for not_found_player in not_found_players_list:

                        not_found_players_message += not_found_player.name
                        not_found_players_message += ', '

                    not_found_players_message = not_found_players_message[:-2]
                    not_found_players_message += ' not found'

                    await ctx.send(not_found_players_message, delete_after=600)

            else:
                await ctx.send("You're not in a voice channel", delete_after=10)

        else:
            for member_name in args:
                member = discord.utils.find(lambda x: x.display_name.lstrip(' ◦◊❃⌇୭૬৸৶৯ৡঙঐ') ==
                                            member_name, ctx.guild.members)
                if member:
                    founded_player = sheets.find_player(member)
                    if founded_player:
                        embed = mmdiscord.form_player_embed(founded_player)
                        await ctx.send(embed=embed, delete_after=600)
                    else:
                        await ctx.send(('No player %s found' % member.display_name.lstrip(' ◦◊❃⌇୭૬৸৶৯ৡঙঐ')),
                                       delete_after=10)
                else:
                    message = 'No discord user %s found' % member_name
                    await ctx.send(message, delete_after=10)
        await ctx.message.delete()

    @commands.command(brief='Use !mm reg (main class) (secondary class) (clan name)')
    @member()
    async def reg(self, ctx, *args):
        print(str(ctx.message.author), ': ', str(ctx.message.content))
        member = ctx.message.author
        correct_request = True

        if not len(args) == 1:
            if len(args) == 2 or len(args) == 3:

                if not args[0] in role_fix_names:
                    await ctx.send('No such role ' + args[0], delete_after=10)
                    correct_request = False

                elif not args[1] in role_fix_names:
                    await ctx.send('No such role ' + args[1], delete_after=10)
                    correct_request = False

                elif sheets.role_fix_names(args[0]) == sheets.role_fix_names(args[1]):
                    await ctx.send('Classes should be different', delete_after=10)
                    correct_request = False

            if len(args) == 3 and correct_request:
                if args[2] not in clan_list:
                    await ctx.send('No such clan ' + args[2] + ' in the list', delete_after=10)
                    correct_request = False
            else:
                if len(args) > 3:
                    await ctx.send('Too many arguments', delete_after=10)
                    correct_request = False
        else:
            await ctx.send('2 Classes required!', delete_after=10)
            correct_request = False

        if correct_request:
            if not sheets.find_player(member):
                sheets.add_player(member, *args)
                await ctx.send('Player ' + member.display_name + ' added')
            else:
                await ctx.send('Player ' + member.display_name + ' already exists, use !mm class and !mm clan',
                               delete_after=10)
        await ctx.message.delete()

    @commands.command(brief='Starts Matchmaking, 12 players needed in a voice channel')
    @member()
    async def start(self, ctx):
        if self.mm_starts:
            return
        self.mm_starts = True

        print(str(ctx.message.author), ': ', str(ctx.message.content))

        if not ctx.channel.name == team_building_text_channel_name:
            print('Wrong text channel')
            return

        if not ctx.author.voice.channel.name == team_building_voice_channel_name:
            print('Wrong voice channel')
            return

        if ctx.author.voice:
            voice_members = ctx.author.voice.channel.members
            players_amount = len(voice_members)

            if players_amount < 12:
                await ctx.send('Not enough players, need ' + str(12 - players_amount) + ' more', delete_after=10)
            else:

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
                        await ctx.send('No free voice channels found')
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

        else:
            await ctx.send('You are not in a voice channel', delete_after=10)

        await ctx.message.delete()
        self.mm_starts = False

    @commands.command(brief='Updates MMR')
    @admin()
    async def update(self, ctx):
        print(str(ctx.message.author), ': ', str(ctx.message.content))
        print('Updating...')
        sheets.insert_formulas()
        await ctx.send('MMR updated!', delete_after=10)
        await ctx.message.delete()

    @commands.command(brief='Moves everyone to Team Building channel, only for modders')
    @moder()
    async def reset(self, ctx):

        print(str(ctx.message.author), ': ', str(ctx.message.content))
        await ctx.message.delete()

        if not (ctx.author.voice.channel.name in (team2_voice_channel_name, team1_voice_channel_name)):
            print('Wrong voice channel')
            return

        direct_channel = discord.utils.find(lambda x: x.name == team_building_voice_channel_name,
                                            ctx.channel.category.channels)
        team1_channel = discord.utils.find(lambda x: x.name == team1_voice_channel_name,
                                           ctx.channel.category.channels)
        team2_channel = discord.utils.find(lambda x: x.name == team2_voice_channel_name,
                                           ctx.channel.category.channels)

        for member1 in team1_channel.members:
            await member1.move_to(direct_channel)
            await asyncio.sleep(0.3)
        for member2 in team2_channel.members:
            await member2.move_to(direct_channel)
            await asyncio.sleep(0.3)

        await ctx.send('Game reset', delete_after=20)

    @commands.command(brief='Locks MMR', name='lockmmr')
    @founder()
    async def new_rating_system(self, ctx):
        print(str(ctx.message.author), ': ', str(ctx.message.content))
        print('Updating...')
        sheets.replace_formulas_with_values()
        await ctx.send('MMR locked')


def setup(bot):
    bot.add_cog(Matchmaking(bot))
