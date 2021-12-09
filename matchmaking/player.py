import random


class Player:
    discord_id = ''

    def __init__(self, stats):
        self.mmr = stats['mmr']
        self.main = stats['main']
        self.secondary = stats['secondary']
        self.nickname = stats['nickname']
        self.discord_id = stats['discord_id']
        self.clan = stats['clan']
        self.top = stats['top']
        self.matches = stats['matches']
        self.wins = stats['wins']
        self.winrate = stats['winrate']
        self.rounds = stats['rounds']
        self.assists = stats['assists']
        self.sr = stats['sr']
        self.mvp = stats['mvp']
        self.kills = stats['kills']
        self.ar = stats['ar']
        self.kr = stats['kr']
        self.mvp_rate = stats['mvp_rate']
        self.score = stats['score']
        self.igl = stats['igl']
        self.country = stats['country']
        self.kar = stats['kar']


def form_random_players():
    nicks = ['Quadri', 'Relynar', 'Walker', 'Artemeis', 'Forsee', 'Silver',
             'Zik', 'Dovmont', 'Ricardo', 'ReD_WaR', 'Black Devil', 'Chao Persik']

    roles = {
        1: ('inf', 'cav'),
        2: ('inf', 'arch'),
        3: ('cav', 'inf'),
        4: ('cav', 'arch'),
        5: ('arch', 'inf'),
        6: ('arch', 'cav'),
    }

    player_list = []

    for nick in nicks:
        player_roles = roles[random.randrange(1, 7)]
        stats = {
            'nickname': nick,
            'mmr': random.randrange(500, 5000),
            'main': player_roles[0],
            'secondary': player_roles[1],
            'discord_id': random.randrange(1000000, 10000000),
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
        player_list.append(Player(stats))
    return player_list
