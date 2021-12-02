import itertools


class Match:

    players = []
    cav = []
    arch = []
    inf = []
    team1 = []
    team2 = []
    mmr_diff = 0
    team1_avg = 0
    team2_avg = 0

    def __init__(self, player_list):
        # copy player objects !!!
        self.players = player_list[:]
        self.team1 = []
        self.team2 = []
        self.cav = []
        self.arch = []
        self.inf = []
        self.team1_avg = 0
        self.team2_avg = 0
        self.mmr_diff = 0


    def fuck_you_you_wont_play_your_main(self, role, amount):
        # amount of players to fuck

        if role == 'cav':
            self.cav.sort(key=lambda x: x.mmr, reverse=True)

            for player in range(amount):
                if self.cav[-1].secondary == 'arch':
                    self.players[self.players.index(self.cav[-1])].main = 'inf'
                    self.players[self.players.index(self.cav[-1])].secondary = 'arch'

                else:
                    self.players[self.players.index(self.cav[-1])].main = 'inf'
                    self.players[self.players.index(self.cav[-1])].secondary = 'cav'
                self.cav.pop()

        else:
            self.arch.sort(key=lambda x: x.mmr, reverse=True)

            for noobs in range(amount):
                self.players[self.players.index(self.arch[-1])].main = 'inf'
                self.arch.pop()

    def set_roles(self):
        cav_mains = 0
        arch_mains = 0
        players_reserve = self.players[:]

        for player in self.players:
            if player.main == 'cav':
                self.cav.append(player)
                cav_mains += 1

        if cav_mains > 4:
            self.fuck_you_you_wont_play_your_main('cav', cav_mains - 4)

        elif cav_mains == 1 or cav_mains == 3:

            temp_secondary_cav_list = []

            for player in self.players:
                if player.secondary == 'cav':
                    # both main and secondary can't be cav
                    temp_secondary_cav_list.append(player)
            if temp_secondary_cav_list:
                temp_secondary_cav_list.sort(key=lambda x: x.mmr)
                self.players[self.players.index(temp_secondary_cav_list[0])].main = 'cav'
                self.cav.append(temp_secondary_cav_list[0])

            else:
                self.fuck_you_you_wont_play_your_main('cav', 1)

        self.players = list(filter(lambda x: x.main != 'cav', self.players))

        for player in self.players:
            if player.main == 'arch':
                self.arch.append(player)
                arch_mains += 1

        if arch_mains > 4:
            self.fuck_you_you_wont_play_your_main('arch', arch_mains - 4)
        elif arch_mains == 1:
            temp_secondary_arch_list = []

            for player in self.players:
                if player.secondary == 'arch':
                    temp_secondary_arch_list.append(player)

            if temp_secondary_arch_list:
                temp_secondary_arch_list.sort(key=lambda x: x.mmr)
                self.players[self.players.index(temp_secondary_arch_list[0])].main = 'arch'
                self.arch.append(temp_secondary_arch_list[0])

            else:
                self.fuck_you_you_wont_play_your_main('arch', 1)

        elif arch_mains == 3:
            self.fuck_you_you_wont_play_your_main('arch', 1)

        self.inf = list(filter(lambda x: x.main == 'inf', self.players))
        self.players = players_reserve

    def make_teams(self):
        cav_mmr = 0
        arch_mmr = 0
        inf_mmr = 0
        cav_mmr_diff = 0
        arch_mmr_diff = 0
        inf_mmr_diff = 0

        for player in self.cav:
            cav_mmr += player.mmr
        for player in self.arch:
            arch_mmr += player.mmr
        for player in self.inf:
            inf_mmr += player.mmr

        temp_mmr = 0
        for player in make_best_combs(self.cav, 0):
            temp_mmr += player.mmr
        cav_mmr_diff = abs((cav_mmr / 2) - temp_mmr) * 2

        temp_mmr = 0
        for player in make_best_combs(self.arch, 0):
            temp_mmr += player.mmr
        arch_mmr_diff = abs((arch_mmr / 2) - temp_mmr) * 2

        temp_mmr = 0
        for player in make_best_combs(self.inf, 0):
            temp_mmr += player.mmr
        inf_mmr_diff = abs((inf_mmr / 2) - temp_mmr) * 2

        classes = [(self.cav, cav_mmr_diff), (self.arch, arch_mmr_diff), (self.inf, inf_mmr_diff)]
        classes.sort(reverse=True, key=lambda x: x[1])
        sorted_classes = [classes[0][0], classes[1][0], classes[2][0]]
        mmr_correct = 0

        for player_class in sorted_classes:
            for player in make_best_combs(player_class, mmr_correct):
                self.team1.append(player)
            for player in player_class:
                if player not in self.team1:
                    self.team2.append(player)

            team1_mmr = 0
            for player in self.team1:
                team1_mmr += player.mmr
            team2_mmr = 0
            for player in self.team2:
                team2_mmr += player.mmr
            mmr_correct = team1_mmr - team2_mmr

    def calc_mmr_diff(self):
        team1_mmr = 0
        team2_mmr = 0
        for player in self.team1:
            team1_mmr += player.mmr
        for player in self.team2:
            team2_mmr += player.mmr
        self.mmr_diff = abs(team1_mmr - team2_mmr)
        self.team2_avg = team2_mmr // 6
        self.team1_avg = team1_mmr // 6

    def sort_teams_by_mmr(self):
        self.team1.sort(key=lambda x: x.mmr, reverse=True)
        self.team2.sort(key=lambda x: x.mmr, reverse=True)

    def reset(self):

        self.players = []
        for player1 in self.team1:
            self.players.append(player1)
        for player2 in self.team2:
            self.players.append(player2)

        self.team1 = []
        self.team2 = []
        self.cav = []
        self.arch = []
        self.inf = []
        self.team1_avg = 0
        self.team2_avg = 0
        self.mmr_diff = 0


def make_best_combs(classname, mmr_correct):

    class_mmr = mmr_correct
    best_players = ()

    for player in classname:
        class_mmr += player.mmr
    best_mmr_diff = 100000000000
    for players in itertools.combinations(classname, len(classname)//2):
        team1_mmr = mmr_correct

        for player in players:
            team1_mmr += player.mmr
        team2_mmr = class_mmr - team1_mmr
        mmr_diff = abs(team1_mmr - team2_mmr)

        if mmr_diff < best_mmr_diff:
            best_players = players
            best_mmr_diff = mmr_diff

    return best_players
