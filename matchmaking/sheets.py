import gspread
from oauth2client.service_account import ServiceAccountCredentials
from settings import *
from matchmaking import player


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

classes_colors = {
        'Infantry': infantry_color,
        'Archer': archer_color,
        'Cavalry': cavalry_color
    }


def find_player(discord_user):
    player_id = str(discord_user.id)
    id_list = sheet.col_values(stat_cols['discord_id'])

    if player_id in id_list:
        player_row = sheet.row_values(id_list.index(player_id) + 1)
    else:
        return None
    print(player_row)

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
        clan_name = '[' + clan_name + ']'

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
            cell.value = mmr_sheets_formula % (cell.row, cell.row, cell.row, cell.row, cell.row, cell.row)

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
