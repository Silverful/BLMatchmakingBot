from screens.screen import Screen
import pytesseract
import cv2 as cv

pytesseract.pytesseract.tesseract_cmd = \
            'C:\\Users\\feodo\\PycharmProjects\\Tesseract-OCR\\tesseract.exe'


for image in range(1):
    screen_no = str(image + 30)
    screen = cv.imread('data\\images\\screen%s.png' % screen_no)
    screen = Screen(screen)
    screen.split_by_teams()
    screen.get_factions()
    screen.find_score()
    fac_debug = 'Aserai'

    print('\n')
    print('Screen %s' % (image+1))

    print('Team 1\n')
    players = screen.get_player_data(1, screen.team1_fac)
    for player in players:
        print(player['name'], player['score'], player['assists'], player['kills'])

    print('Team 2\n')
    players = screen.get_player_data(2, screen.team2_fac)
    for player in players:
        print(player['name'], player['score'], player['assists'], player['kills'])
    print(str(screen.team1_fac).ljust(10), str(screen.team1_score).ljust(3), str(screen.team2_score).ljust(3), screen.team2_fac)
    print(str(screen.rounds))



for image in range(0):
    screen_no = str(image + 1)
    screen = cv.imread('data\\images\\screen%s.png' % screen_no)
    screen = Screen(screen)
    screen.split_by_teams()
    screen.get_factions()
    screen.find_score()
    print(('Screen %s' % str(image + 1)).ljust(15), screen.team1_fac.ljust(10),
          screen.team1_score.ljust(10), screen.team2_score.ljust(10), screen.team2_fac.ljust(10))
