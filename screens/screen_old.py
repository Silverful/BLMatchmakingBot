import cv2 as cv
import pytesseract
from screens import ocvprep
from screens.ocvprep import thresholding, is_dead
from screens.prep_settings import faction_list
from screens.errors import *


class Screen:

    def __init__(self, img):
        #pytesseract.pytesseract.tesseract_cmd = \
         #   'C:\\Users\\feodo\\PycharmProjects\\Tesseract-OCR\\tesseract.exe'
        #self.screen = cv.imread(img)
       # pytesseract.pytesseract.tesseract_cmd = "/app/.apt/usr/bin/tesseract"
        self.screen = img
        self.screen_raw = self.screen[::]
        self.stat_len = None
        self.left_pos = [0, 0]
        self.right_pos = [0, 0]
        self.screenW = self.screen.shape[1]
        self.screenH = self.screen.shape[0]
        self.team1 = None
        self.team2 = None
        self.pingW = None
        self.pingH = None
        self.team1heights = None
        self.team2heights = None
        self.got = False
        self.team1_fac = None
        self.team2_fac = None
        self.team1_score = None
        self.team2_score = None


    def find_score(self):
        scores = self.screen_raw[self.left_pos[1] - self.screenW//17:self.left_pos[1] - self.screenW//50,
                               self.screenW * 45 // 100: self.screenW * 54 // 100]

        scoreconfig = r'--oem 3 --psm 6 outputbase digits'

        score1 = scores[:, :scores.shape[1] * 45 // 100]
        score2 = scores[:, scores.shape[1] * 56 // 100:]
        score1 = ocvprep.fullprep(score1)
        score2 = ocvprep.fullprep(score2)
        score1 = ocvprep.find_box(score1, bottom=True, indent=15)
        score2 = ocvprep.find_box(score2, bottom=True, indent=15)
        score1_data = pytesseract.pytesseract.image_to_data(score1, config=scoreconfig)
        score2_data = pytesseract.pytesseract.image_to_data(score2, config=scoreconfig)
        data = []
        for x, b in enumerate(score1_data.splitlines()):
            if x != 0:
                b = b.split()
                if len(b) == 12:
                    data.append(b[11])
        for x, b in enumerate(score2_data.splitlines()):
            if x != 0:
                b = b.split()
                if len(b) == 12:
                    data.append(b[11])

        self.team1_score = data[0]
        self.team2_score = data[1]

    def split_by_teams(self):
        boxes = pytesseract.image_to_data(ocvprep.fullprep(self.screen, scale=4, thresh=130))

        ping1data = None
        ping2data = None
        score1data = None
        score2data = None

        for x, b in enumerate(boxes.splitlines()):
            if x != 0:
                b = b.split()
                if len(b) == 12:
                    if b[11] == 'Ping':
                        x, y, w, h = int(b[6]), int(b[7]), int(b[8]), int(b[9])
                        if not ping1data:
                            ping1data = x//4, y//4, w//4, h//4
                        elif (not ping2data) and (y//4 > ping1data[1]-25) and (y//4 < ping1data[1] + 25):
                            ping2data = x//4, y//4, w//4, h//4
        if not ping2data:
            raise CantFindPing

        leftpingdata = ping2data if ping1data[0] > ping2data[0] else ping1data

        for x, b in enumerate(boxes.splitlines()):
            if x != 0:
                b = b.split()
                if len(b) == 12:
                    if b[11] == 'Score':
                        x, y, w, h = int(b[6]), int(b[7]), int(b[8]), int(b[9])
                        if not score1data:
                            score1data = x//4, y//4, w//4, h//4
                        elif (not score2data) and (y//4 > score1data[1]-25) and (y//4 < score1data[1] + 25):
                            score2data = x//4, y//4, w//4, h//4
        if not score2data:
            raise CantFindScore

        rightscoredata = score1data if score1data[0] > score2data[0] else score2data

        img_w = (rightscoredata[0]+rightscoredata[2] - leftpingdata[0]) * 103 // 100

        pingline = self.screen[leftpingdata[1] + leftpingdata[3] * 3: leftpingdata[1] + leftpingdata[3] + img_w // 3,
                               leftpingdata[0]: leftpingdata[0] + leftpingdata[2]]

        pingline = ocvprep.make_gray(pingline)
        pingline = cv.resize(pingline, [pingline.shape[1] * 4, pingline.shape[0] * 4])
        pingline = cv.bilateralFilter(pingline, 4, 40, 60)
        pingline = ocvprep.contrast(pingline, contrast=3)
        pingline = thresholding(pingline, 100, 255)

        score_config = r'--oem 3 --psm 6'

        pingdata = pytesseract.pytesseract.image_to_data(pingline, config=score_config)
        data = []
        lastping_data = None
        for x, b in enumerate(pingdata.splitlines()):
            if x != 0:
                b = b.split()
                if len(b) == 12:
                    data.append(b[11])
            if len(data) == 6:
                lastping_data = b
        if not lastping_data:
            return CantFindHeight

        img_h = (int(lastping_data[7]) + int(lastping_data[9]) * 31 // 10) // 4 + leftpingdata[3] * 3

        self.screen = self.screen[leftpingdata[1]: leftpingdata[1] + img_h, leftpingdata[0]: leftpingdata[0] + img_w]

        self.stat_len = img_w
        self.left_pos = [leftpingdata[0], leftpingdata[1]]
        self.right_pos = [rightscoredata[0] + rightscoredata[2], rightscoredata[1]]
        img_h, img_w, _ = self.screen.shape
        self.screen = self.screen[img_h // 7:, :]
        img_h, img_w, _ = self.screen.shape
        self.team1 = self.screen[:, img_w // 8: (img_w // 8) + (img_w * 10 // 28)]
        self.team2 = self.screen[:, img_w * 100 // 158: (img_w * 10 // 14) + (img_w * 10 // 28)]

        return False

    def get_factions(self):

        fac1 = self.screen_raw[self.left_pos[1] - (self.stat_len * 7 // 100):
                               self.left_pos[1] - (self.stat_len * 36 // 1000),
                               self.left_pos[0]:
                               self.left_pos[0] + self.stat_len * 11 // 100]

        fac2 = self.screen_raw[self.right_pos[1] - (self.stat_len * 7 // 100):
                               self.right_pos[1] - (self.stat_len * 36 // 1000),
                               self.right_pos[0] - self.stat_len * 9 // 100:
                               self.right_pos[0] + self.stat_len * 3 // 100]

        fac2 = ocvprep.fullprep(fac2, thresh=160)
        fac2 = ocvprep.remove_noise(fac2)
        fac2 = ocvprep.find_box(fac2, bottom=True, indent=20)
        fac2 = cv.resize(fac2, None, fx=0.25, fy=0.25)

        fac1 = ocvprep.fullprep(fac1, thresh=160)
        fac1 = ocvprep.remove_noise(fac1)
        fac1 = ocvprep.find_box(fac1, bottom=True, indent=20)
        fac1 = cv.resize(fac1, None, fx=0.25, fy=0.25)

        team1fac = pytesseract.pytesseract.image_to_data(fac1)
        team2fac = pytesseract.pytesseract.image_to_data(fac2)
        for x, b in enumerate(team1fac.splitlines()):
            if x != 0:
                b = b.split()
                if len(b) == 12:
                    if b[11] in faction_list:
                        self.team1_fac = b[11]
        for x, b in enumerate(team2fac.splitlines()):
            if x != 0:
                b = b.split()
                if len(b) == 12:
                    if b[11] in faction_list:
                        self.team2_fac = b[11]

    def get_player_data(self, team_no, fac=None):
        self.got = True
        if team_no == 1:
            team = self.team1
            fac = self.team1_fac
        else:
            team = self.team2
            fac = self.team2_fac

        team1h = team.shape[0]
        rowh = team1h // 6
        stats_config = r'--oem 3 --psm 6 outputbase digits'
        score_config = r'--oem 3 --psm 6 outputbase digits'
        team1_data = []
        names = []
        scores = []
        kills = []
        assists = []
        errors = []
        bright_player = 0
        if team_no == 1:
            brights = []
            for n in range(6):
                player_string = team[rowh * n: rowh * (n + 1), :]
                player_name = player_string[:, :player_string.shape[1] * 2 // 5]
                brights.append(ocvprep.isbright(player_string))
            bright_player = max(enumerate(brights), key=lambda br: br[1])[0]
        else:
            bright_player = 10

        for n in range(6):

            player_string = team[rowh * n: rowh * (n + 1), :]
            player_name = player_string[:, :player_string.shape[1] * 2 // 5]
            player_kills = player_string[:, player_string.shape[1] * 43 // 100:player_string.shape[1] * 26 // 50]
            player_assists = player_string[:, player_string.shape[1] * 26 // 50:player_string.shape[1] * 32 // 50]
            player_scores = player_string[:, player_string.shape[1] * 4 // 5:player_string.shape[1] * 98 // 100]

            player_kills = cv.resize(player_kills, [player_kills.shape[1] * 4, player_kills.shape[0] * 4])
            player_scores = cv.resize(player_scores, [player_scores.shape[1] * 4, player_scores.shape[0] * 4])
            player_assists = cv.resize(player_assists, [player_assists.shape[1] * 4, player_assists.shape[0] * 4])
            player_name = cv.resize(player_name, [player_name.shape[1] * 5, player_name.shape[0] * 5])
            error = []
            brightness_kills_for_error = ocvprep.isbright(player_kills)
            brightness_assists_for_error = ocvprep.isbright(player_assists)
            try:
                player_name = ocvprep.make_gray(player_name)

                #player_name = ocvprep.contrast(player_name, brightness=0.9)

                player_kills = ocvprep.make_gray(player_kills)
                player_scores = ocvprep.make_gray(player_scores)
                player_assists = ocvprep.make_gray(player_assists)
            except:
                raise MakingGrayError

            player_kills = cv.bilateralFilter(player_kills, 4, 40, 60)
            player_scores = cv.bilateralFilter(player_scores, 4, 40, 60)
            player_assists = cv.bilateralFilter(player_assists, 4, 40, 60)
            player_name = cv.bilateralFilter(player_name, 1, 1, 20)

            player_name = ocvprep.contrast(player_name, contrast=3)
            player_kills = ocvprep.contrast(player_kills, contrast=2)
            player_scores = ocvprep.contrast(player_scores, contrast=2)
            player_assists = ocvprep.contrast(player_assists, contrast=2)

            if is_dead(player_string):

                player_kills = thresholding(player_kills, 100, 255)
                player_scores = thresholding(player_scores, 100, 255)
                player_assists = thresholding(player_assists, 100, 255)
                player_name = thresholding(player_name, 160, 255)

            else:
                player_name = ocvprep.remove_noise(player_name)
                player_kills = thresholding(player_kills, 170, 255)
                player_scores = thresholding(player_scores, 170, 255)
                player_assists = thresholding(player_assists, 170, 255)
                player_name = thresholding(player_name, 170, 255)


            player_scores = ocvprep.remove_noise(player_scores)
            player_kills = ocvprep.remove_noise(player_kills)
            player_assists = ocvprep.remove_noise(player_assists)
            player_name = ocvprep.remove_noise(player_name)

            try:
                player_scores = ocvprep.find_box(player_scores, indent=6)
                player_kills = ocvprep.find_box(player_kills, indent=3)
                player_assists = ocvprep.find_box(player_assists, indent=3)
                #player_name = ocvprep.find_box(player_name, bottom=True, indent=40)
            except:
                raise BoxesError

            player_name = cv.GaussianBlur(player_name, (5, 5), 0)
            player_scores = ocvprep.remove_noise(player_scores)
            player_kills = cv.GaussianBlur(player_kills, (1, 1), 0)
            player_assists = cv.GaussianBlur(player_assists, (1, 1), 0)
            #if is_dead(player_string):
             #   cv.imshow('adf', player_name)
              #  cv.waitKey(0)

            score = pytesseract.image_to_data(player_scores, config=score_config)
            kill = pytesseract.image_to_data(player_kills, config=stats_config)
            assist = pytesseract.image_to_data(player_assists, config=stats_config)
            name = pytesseract.image_to_string(player_name)
            while ']' in name:
                name = name[name.index(']')+1:]
            name = name.rstrip().lstrip()
            names.append(name)
            data = []
            for x, b in enumerate(score.splitlines()):
                if x != 0:
                    b = b.split()
                    if len(b) == 12:
                        data.append(b[11])
            if data:
                scores.append(data)
            else:
                scores.append('-')
            data = []

            for x, b in enumerate(kill.splitlines()):
                if x != 0:
                    b = b.split()
                    if len(b) == 12:
                        data.append(b[11])
            if data:
                kills.append(data)
            else:
                kills.append('-')
                if not error:
                    error.append(is_dead(player_string))
                    error.append(brightness_kills_for_error)
            data = []

            for x, b in enumerate(assist.splitlines()):
                if x != 0:
                    b = b.split()
                    if len(b) == 12:
                        data.append(b[11])
            if data:
                assists.append(data)
            else:
                assists.append('-')
            error.append(is_dead(player_string))
            error.append(brightness_assists_for_error)
            errors.append(error)

        for name, kills, assists, score, error in zip(names, kills, assists, scores, errors):
            player = []
            if ']' in name:
                #player = [(''.join(name.split(']')[1:])).lstrip()]
                player = [name]
                pass
            else:
                player = [name]
            name.replace('\n', '')
            name.lstrip(' ')
            for stat in kills:
                if stat:
                    player.append(stat)
                else:
                    player.append('-')
            for stat in assists:
                if stat:
                    player.append(stat)
                else:
                    player.append('-')

            if score:
                player.append(score[0])
            else:
                player.append('-')
            for err in error:
                player.append(err)
            team1_data.append(player)
        result = []
        try:
            if team_no == 1:
                faction = self.team1_fac
                rw = int(self.team1_score)
            else:
                faction = self.team2_fac
                rw = int(self.team2_score)
            if rw == 3:
                won = 1
            else:
                won = 0
        except:
            raise CantFindScore
        rounds = int(self.team1_score) + int(self.team2_score)
        for index, item in enumerate(team1_data):
            result_player = {
                'name': item[0],
                'kills': item[1],
                'assists': item[2],
                'score': item[3],
                'faction': faction,
                'rw': rw,
                'won': won,
                'mvp': 0,
                'rounds': rounds
            }
            result.append(result_player)
            string = item[0].lstrip('').ljust(30)

            if item[4]:
                item[4] = 'Dead'
            for stat in item[1:4]:

                if stat:
                    string += str(stat).ljust(6)
                else:
                    string += '-'.ljust(6)

        return result



result_player = {
                'name': item[0],
                'kills': item[1],
                'assists': item[2],
                'score': item[3],
                'faction': faction,
                'rw': rw,
                'won': won,
                'mvp': 0,
                'rounds': self.rounds
            }

