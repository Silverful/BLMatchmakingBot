import gspread
from oauth2client.service_account import ServiceAccountCredentials
from settings import *
from matchmaking import player
import numpy as np


def clan_fix_names(clan_name):
    if clan_name in ['None', 'no', 'free', 'Free', 'none', 'No']:
        return 'Free'
    else:
        return '[%s]' % clan_name


def role_fix_names(sent_role_name):
    if sent_role_name in ['arch', 'Arch', 'Archer', 'archer', 'arc', 'Arc']:
        return 'Archer'
    elif sent_role_name in ['inf', 'Inf', 'Infantry', 'infantry']:
        return 'Infantry'
    else:
        return 'Cavalry'


def fix_div_0(sent_value):
    if sent_value == '#DIV/0!':
        return '0'
    else:
        return sent_value


scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json')
client_obj = gspread.authorize(creds)
sheet = client_obj.open(playerbase).worksheet(stats_worksheet)
screen_sheet = client_obj.open(playerbase).worksheet(screens_worksheet)
test_sheet = client_obj.open(playerbase).worksheet(test_worksheet)

classes_colors = {
        'Infantry': infantry_color,
        'Archer': archer_color,
        'Cavalry': cavalry_color
    }


def add_screen(players, screen_url):
    max_row = str(len(screen_sheet.get_all_values()) + 1)
    start_row = int(max_row)
    players_no = len(players)
    cellrange = screen_sheet.range('A%s:M%s' % (start_row, start_row))
    regged_players_no = str(len(sheet.get_all_values()))
    nicks = []

    nick_cells = sheet.range('B2:B%s' % regged_players_no)
    games_cells = sheet.range('I2:I%s' % regged_players_no)

    all_players_found = True
    for nick in nick_cells:
        nicks.append(nick.value)

    for player_no, data in enumerate(players):
        current_row = str(start_row + player_no)
        name_to_write = data['name']
        stats_player_row = 0
        nick_found = False
        for index, nick in enumerate(nicks):
            if (nick.lower() in data['name'].lower()) and len(nick) > 3:
                name_to_write = nick
                nick_found = True
                stats_player_row = index
        calibrating = '0'
        if not nick_found:
            if 'bulling skirmish' in data['name'].lower():
                name_to_write = 'Chao Persik'
            else:
                all_players_found = False
        else:
            games_played = games_cells[stats_player_row].value
            if int(games_played) > 10:
                calibrating = 0
            else:
                calibrating = 10 - int(games_played)


        row = [
            '-',
            name_to_write,
            1,
            data['won'] if str(data['won']).lstrip('-').isdigit() else '-',
            data['rounds'] if str(data['rounds']).lstrip('-').isdigit() else '-',
            data['kills'] if str(data['kills']).lstrip('-').isdigit() else '-',
            data['assists'] if str(data['assists']).lstrip('-').isdigit() else '-',
            data['score'] if str(data['score']).lstrip('-').isdigit() else '-',
            data['mvp'] if str(data['mvp']).lstrip('-').isdigit() else '-',
            data['faction'],
            '',
            screen_url,
            calibrating
        ]

        cellrow = screen_sheet.range('A%s:M%s' % (current_row, current_row))
        for index, stat in enumerate(cellrow):
            stat.value = row[index]
        cellrange.extend(cellrow)
    screen_sheet.update_cells(cellrange, value_input_option='USER_ENTERED')
    return all_players_found

def clr_sheet():
    rangesh = test_sheet.range('A2:AA100')
    for cell in rangesh:
        cell.value = ''
    test_sheet.update_cells(rangesh)

def find_player(discord_user):
    player_id = str(discord_user.id)
    id_list = sheet.col_values(stat_cols['discord_id'])

    if player_id in id_list:
        player_row = sheet.row_values(id_list.index(player_id) + 1)
    else:
        return None


    class_fix = {
        'Cavalry': 'cav',
        'Archer': 'arch',
        'Infantry': 'inf'
    }

    stats = {
        'discord_id': player_id,
        'mmr': int(player_row[stat_cols['mmr'] - 1]),
        'main': class_fix[player_row[stat_cols['main'] - 1]],
        'secondary': class_fix[player_row[stat_cols['secondary'] - 1]],
        'nickname': player_row[stat_cols['nickname'] - 1],
        'clan': str(player_row[stat_cols['clan'] - 1]),
        'top': str(player_row[stat_cols['top'] - 1]),
        'matches': str(player_row[stat_cols['matches'] - 1]),
        'wins': str(player_row[stat_cols['wins'] - 1]),
        'winrate': fix_div_0(str(player_row[stat_cols['winrate'] - 1])),
        'rounds': str(player_row[stat_cols['rounds'] - 1]),
        'assists': str(player_row[stat_cols['assists'] - 1]),
        'mvp': str(player_row[stat_cols['mvp'] - 1]),
        'kills': str(player_row[stat_cols['kills'] - 1]),
        'ar': str(player_row[stat_cols['ar'] - 1]),
        'kr': str(player_row[stat_cols['kr'] - 1]),
        'sr': str(player_row[stat_cols['sr'] - 1]),
        'mvp_rate': str(player_row[stat_cols['mvp_rate'] - 1]),
        'score': str(player_row[stat_cols['score'] - 1]),
        'igl': str(player_row[stat_cols['igl'] - 1]),
        'country': str(player_row[stat_cols['country'] - 1]),
        'kar': str(player_row[stat_cols['kar'] - 1])

    }

    return player.Player(stats)


def add_player(discord_member, main_class='Infantry', secondary_class='Archer', clan_name='Free'):

    main_class = role_fix_names(main_class)
    secondary_class = role_fix_names(secondary_class)

    if clan_name in ['None', 'no', 'free', 'Free', 'none', 'No']:
        clan_name = 'Free'
    else:
        clan_name = clan_name

    player_row = str(len(sheet.get_all_values()) + 1)
    cell_list = sheet.range('A%s:%s%s' % (player_row, chr(len(stat_cols)+64), player_row))

    index = 0
    new_player_stats = [
        str(int(player_row)-1),
        discord_member.display_name.lstrip(' ◦◊❃⌇୭૬৸৶৯ৡঙঐ'),
        'Zimbabwe',
        '',
        clan_fix_names(clan_name),
        role_fix_names(main_class),
        role_fix_names(secondary_class),
        sheet_formulas['mmr'].format(player_row),
        sheet_formulas['matches'].format(player_row),
        sheet_formulas['wins'].format(player_row),
        sheet_formulas['winrate'].format(player_row),
        sheet_formulas['rounds'].format(player_row),
        sheet_formulas['kills'].format(player_row),
        sheet_formulas['kr'].format(player_row),
        sheet_formulas['assists'].format(player_row),
        sheet_formulas['ar'].format(player_row),
        sheet_formulas['kar'].format(player_row),
        sheet_formulas['score'].format(player_row),
        sheet_formulas['sr'].format(player_row),
        sheet_formulas['mvp'].format(player_row),
        sheet_formulas['mvp_rate'].format(player_row),
        str(discord_member.id)
    ]

    for cell in cell_list:
        cell.value = new_player_stats[index]
        index += 1
    sheet.update_cells(cell_list, value_input_option='USER_ENTERED')
    sheet.format(('A%s:%s%s' % (player_row, chr(len(stat_cols)+64), player_row)), {'textFormat': text_format})
    sheet.format('B%s:B%s' % (player_row, player_row), {"backgroundColor": classes_colors[main_class]})

#    screen_sheet.append_row([0, discord_member.name, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'Registered'])
    sheet.sort((stat_cols['mmr'], 'des'), range='B2:%s%s' % (chr(len(stat_cols)+64), str(len(sheet.get_all_values()))))


def insert_formulas():
    sheet_len = len(screen_sheet.get_all_values())

    mmr_cells = screen_sheet.range('K2:K%s' % sheet_len)
    for cell in mmr_cells:
        if cell.value == '':
            cell.value = mmr_sheets_formula % (cell.row, cell.row, cell.row, cell.row, cell.row,
                                               cell.row, cell.row, cell.row, cell.row)

    screen_sheet.update_cells(mmr_cells, value_input_option='USER_ENTERED')
    sheet.sort((stat_cols['mmr'], 'des'), range='B2:%s%s' % (chr(len(stat_cols)+64), str(len(sheet.get_all_values()))))
    print('MMR updated')


def replace_formulas_with_values():
    sheet_len = len(screen_sheet.get_all_values())

    mmr_cells = screen_sheet.range('K2:K%s' % sheet_len)
    for cell in mmr_cells:
        cell.value = int(cell.value)

    screen_sheet.update_cells(mmr_cells, value_input_option='USER_ENTERED')
    print('MMR locked')


def change_clan(discord_member, clan):
    sheet_len = len(sheet.get_all_values())

    cells = sheet.range(('{0}2:{0}%s' % sheet_len).format(chr(stat_cols['discord_id'] + 64)))
    player_row = None

    for cell in cells:
        if str(discord_member.id) == cell.value:
            player_row = cell.row

    if player_row:
        sheet.update('%s%s' % (chr(stat_cols['clan'] + 64), player_row), clan_fix_names(clan))


def change_classes(discord_member, main, secondary):
    sheet_len = len(sheet.get_all_values())
    cells = sheet.range(('{0}2:{0}%s' % sheet_len).format(chr(stat_cols['discord_id'] + 64)))
    player_row = None
    for cell in cells:
        if str(discord_member.id) == cell.value:
            player_row = cell.row
    if player_row:
        sheet.update(('%s%s' % (chr(stat_cols['main'] + 64), player_row)), role_fix_names(main))
        sheet.update('%s%s' % (chr(stat_cols['secondary'] + 64), player_row), role_fix_names(secondary))
   #     sheet.format(('A%s:E%s' % (player_row, player_row)), {'textFormat': text_format})
        sheet.format(('{0}{1}:{0}{1}'.format(chr(stat_cols['nickname'] + 64), player_row)),
                     {"backgroundColor": classes_colors[role_fix_names(main)]})


def change_country(discord_member, country):
    sheet_len = len(sheet.get_all_values())

    cells = sheet.range(('{0}2:{0}%s' % sheet_len).format(chr(stat_cols['discord_id'] + 64)))
    player_row = None

    for cell in cells:
        if str(discord_member.id) == cell.value:
            player_row = cell.row

    if player_row:
        sheet.update('%s%s' % (chr(stat_cols['country'] + 64), player_row), country)


def find_players(discord_users):

    values = sheet.get_values('A:V')
    values = np.array(values)
    players = []
    not_found_users = []

    for discord_user in discord_users:

        discord_user_id = str(discord_user.id)
        values = np.transpose(values)
        found_row = None

        for index, discord_id in enumerate(values[stat_cols['discord_id'] - 1]):
            if str(discord_id) == discord_user_id:
                found_row = index
        values = np.transpose(values)

        if not found_row:
            player_values = [None, None, discord_user.displayname.lstrip(' ◦◊❃⌇୭૬৸৶৯ৡঙঐ'), None, None, None,
                             'Infantry', 'Archer', 3000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, discord_user_id]
            not_found_users.append(discord_user)
        else:
            player_values = values[found_row]
            player_values = np.insert(player_values, 0, None)

        player_to_add = {
            'mmr': int(player_values[8]),
            'discord_id': player_values[22],
            'nickname': player_values[2],
            'main': player_values[6],
            'secondary': player_values[7],
            'clan': player_values[5],
            'top': player_values[1],
            'matches': player_values[9],
            'wins': player_values[10],
            'winrate': player_values[11],
            'rounds': player_values[12],
            'kills': player_values[13],
            'assists': player_values[15],
            'sr': player_values[19],
            'mvp': player_values[20],
            'kr': player_values[14],
            'ar': player_values[16],
            'mvp_rate': player_values[21],
            'score': player_values[18],
            'igl': player_values[4],
            'country': player_values[3],
            'kar': player_values[17],
        }
        player_to_add = player.Player(player_to_add)
        players.append(player_to_add)
    return players, not_found_users
