import os
from pathlib import Path
from dotenv import load_dotenv
try:
    env_path = Path(".") / ".env"
    load_dotenv(dotenv_path=env_path)
finally:
    pass
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", False)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')

DISCORD_BOT_COMMAND_PREFIX = '!mm '

playerbase = 'BL Matchmaking'
stats_worksheet = 'Stats'
screens_worksheet = 'Screens'

team1_voice_channel_name = 'Team #1'
team2_voice_channel_name = 'Team #2'
team3_voice_channel_name = 'Team #3'
team4_voice_channel_name = 'Team #4'
team5_voice_channel_name = 'Team #5'
team6_voice_channel_name = 'Team #6'
team7_voice_channel_name = 'Team #7'
team8_voice_channel_name = 'Team #8'
team_building_voice_channel_name = 'Team building'
team_building_text_channel_name = 'mm-team-building'
queue_voice_channel_name = 'Queue'
hinq_guild_id = 545964006851084290

sort_teams_by = 'MMR'    # 'MMR' or 'Class'
moderator_role_name = 'Moderator'
admin_role_name = 'Administrator'
founder_role_name = 'Founder'
player_role_name = 'Bannerlord Matchmaking Player'
sheet_edit_perms = admin_role_name


clan_list = ['HINQ', 'BT', 'T', 'RS', 'Hawk', 'HV', 'FFS']
no_clan = ['None', 'no', 'free', 'Free', 'none', 'No']
role_fix_names = ['arch', 'inf', 'cav', 'Cav', 'Arch', 'Inf', 'Cavalry', 'Archer', 'Infantry', 'cavalry',
                  'archer', 'infantry', 'arc', 'Arc']

waiting_phrases = [
    'Calculating mmr...',
    'Getting user stats...',
    'Balancing cav...',
    'Forming teams...',
    'Insulting Taleworlds on forums...',
    'Muting Varadin...',
    'Increasing your ping...',
    'Deploying Bitcoin miner on your PC...',
    'Crashing game...',
    'DDoSing Taleworlds servers...',
    'Reducing FPS...',
    'Trolling DonNeto'
]

archer_color = {
    'red': 1,
    'green': 0.9,
    'blue': 0.6
}
infantry_color = {
    'red': 0.71,
    'green': 0.84,
    'blue': 0.66
}
cavalry_color = {
    'red': 0.92,
    'green': 0.6,
    'blue': 0.6
}
text_format = {
    'bold': True,
    'fontFamily': 'Calibri',
    'fontSize': 12
}

stat_cols = {
    'mmr': 8,
    'discord_id': 22,
    'nickname': 2,
    'main': 6,
    'secondary': 7,
    'clan': 5,
    'top': 1,
    'matches': 9,
    'wins': 10,
    'winrate': 11,
    'rounds': 12,
    'kills': 13,
    'assists': 15,
    'sr': 19,
    'mvp': 20,
    'kr': 14,
    'ar': 16,
    'mvp_rate': 21,
    'score': 18,
    'igl': 4,
    'country': 3,
    'kar': 17
}

sheet_formulas = {
    'mmr': '=IFERROR(SUM(FILTER(Screens!K:K; Screens!B:B = %s{0})) + 3000; 3000)' % chr(stat_cols['nickname'] + 64),
    'discord_id': None,
    'nickname': None,
    'main': None,
    'secondary': None,
    'clan': None,
    'top': None,
    'matches': '=IFERROR(SUM(FILTER(Screens!C:C; Screens!B:B = %s{0})); "0")' % chr(stat_cols['nickname'] + 64),
    'wins': '=IFERROR(SUM(FILTER(Screens!D:D; Screens!B:B = %s{0})); "0")' % chr(stat_cols['nickname'] + 64),
    'winrate': '=IFERROR(%s{0}/%s{0}; "0")' % (chr(stat_cols['wins'] + 64), chr(stat_cols['matches'] + 64)),
    'rounds': '=IFERROR(SUM(FILTER(Screens!E:E; Screens!B:B = %s{0})); "0")' % chr(stat_cols['nickname'] + 64),
    'kills': '=IFERROR(SUM(FILTER(Screens!F:F; Screens!B:B = %s{0})); "0")' % chr(stat_cols['nickname'] + 64),
    'assists': '=IFERROR(SUM(FILTER(Screens!G:G; Screens!B:B = %s{0})); "0")' % chr(stat_cols['nickname'] + 64),
    'sr': '=IFERROR(%s{0}/%s{0}; "0")' % (chr(stat_cols['score'] + 64), chr(stat_cols['rounds'] + 64)),
    'mvp': '=IFERROR(SUM(FILTER(Screens!I:I; Screens!B:B = %s{0})); "0")' % chr(stat_cols['nickname'] + 64),
    'kr': '=IFERROR(%s{0}/%s{0}; "0")' % (chr(stat_cols['kills'] + 64), chr(stat_cols['rounds'] + 64)),
    'ar': '=IFERROR(%s{0}/%s{0}; "0")' % (chr(stat_cols['assists'] + 64), chr(stat_cols['rounds'] + 64)),
    'mvp_rate': '=IFERROR(%s{0}/%s{0}; "0")' % (chr(stat_cols['mvp'] + 64), chr(stat_cols['rounds'] + 64)),
    'score': '=IFERROR(SUM(FILTER(Screens!H:H; Screens!B:B = %s{0})); "0")' % chr(stat_cols['nickname'] + 64),
    'igl': None,
    'country': None,
    'kar': '=IFERROR((%s{0}+%s{0})/%s{0}; "0")' % (chr(stat_cols['kills'] + 64), chr(stat_cols['assists'] + 64),
                                                   chr(stat_cols['rounds'] + 64))
}

main_mmr_bank = 50
additional_mmr_bank = 150

main_mmr_bank_cell = stats_worksheet + '!$AF$5'
additional_mmr_bank_cell = stats_worksheet + '!$AF$6'

mmr_sheets_formula = '=((D%s * -1) + 1 + QUOTIENT(((D%s - 1) * ' + additional_mmr_bank_cell +\
                     ' * 2); 6) + (2 * ' + main_mmr_bank_cell + ' * D%s) - ' + main_mmr_bank_cell + \
                     ') + QUOTIENT((' + additional_mmr_bank_cell + ' * H%s); SUM(FILTER(H:H; L:L = L%s; D:D = D%s)))'
#    % (row_number x 6)
