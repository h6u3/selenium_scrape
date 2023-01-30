from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException as NSEE
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

import time

lichess = [
           ['https://lichess.org/stat/rating/distribution/ultraBullet', 0],
           ['https://lichess.org/stat/rating/distribution/bullet', 0],
           ['https://lichess.org/stat/rating/distribution/blitz', 0],
           ['https://lichess.org/stat/rating/distribution/rapid', 0],
           ['https://lichess.org/stat/rating/distribution/classical', 0],
           ['https://lichess.org/stat/rating/distribution/chess960', 0],
           ]

chesscom = [
            ['https://www.chess.com/leaderboard/live/bullet', 0] ,
            ['https://www.chess.com/leaderboard/live/blitz', 0] ,
            ['https://www.chess.com/leaderboard/live/rapid', 0] ,
            ['https://www.chess.com/leaderboard/daily', 0] ,
            ['https://www.chess.com/leaderboard/daily/chess960', 0] ,
            ]

#constants for better code read
URL = 0
PLAYER_COUNT = 1

#lichess constants
L_U_BULLET = 0
L_BULLET = 1
L_BLITZ = 2
L_RAPID = 3
L_CLASSICAL = 4
L_CHESS960 = 5

#chesscom constants
C_BULLET = 0
C_BLITZ = 1
C_RAPID = 2
C_DAILY = 3
C_CHESS960 = 4

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")
# chrome_options.headless = True # also works

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

#driver.get(website)
driver.set_window_position(0, 0)
driver.set_window_size(1200, 3000)
ignored_exceptions=(NSEE,StaleElementReferenceException)

def scrape_lichess():
    driver.get('https://lichess.org/')
    L_overall_stat = []
    try:
        l_player = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '//a[@href="/player"]/strong'))).text.replace(",", "")
        #print("players: ", l_player)
        L_overall_stat.append(l_player)
    except TimeoutException:
        print("Timed out waiting for lichess player count to load")
    try:
        l_games = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '//a[@href="/games"]/strong'))).text.replace(",", "")
        #print("games: ", l_games)
        L_overall_stat.append(l_games)
    except TimeoutException:
        print("Timed out waiting for lichess game count to load")
    for pages in lichess:
        driver.get(pages[URL])
        try:
            pages[PLAYER_COUNT] = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '//div[@class="desc"]/div/strong'))).text.replace(",", "")
            #print(pages[URL].split("/")[-1] + ": " + pages[PLAYER_COUNT])
        except TimeoutException:
            print("Timed out waiting for {} player count to load".format(pages[URL].split("/")[-1]))
    return L_overall_stat
        

def scrape_chesscom():
    driver.get('https://www.chess.com/leaderboard')
    C_overall_stat = []
    try:
        c_player = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '(//div[@class="leaderboard-index-sidebar-value"])[1]'))).text.replace(",", "")
        #print("players: ", c_player)
        C_overall_stat.append(c_player)
    except TimeoutException:
        print("Timed out waiting for chesscom player count to load")
    try:
        c_now = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '(//div[@class="leaderboard-index-sidebar-value"])[3]'))).text.replace(",", "")
        #print("playing now: ", c_now)
        C_overall_stat.append(c_now)
    except TimeoutException:
        print("Timed out waiting for chesscom game count to load")
    for pages in chesscom:
        driver.get(pages[URL])
        try:
            pages[PLAYER_COUNT] = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '(//aside[@class="leaderboard-stats-row-aside"])[1]'))).text.replace(",", "")
            #print(pages[URL].split("/")[-1] + ": " + pages[PLAYER_COUNT])
        except TimeoutException:
            print("Timed out waiting for {} player count to load".format(pages[URL].split("/")[-1]))
    return C_overall_stat

def scrape():
    start_time = time.time()
    lichess_stat = scrape_lichess()
    chesscom_stat = scrape_chesscom()
    driver.close()
    date = datetime.today().strftime('%d-%m-%Y')
    time = datetime.now().strftime('%H:%M')
    df = pd.DataFrame({'Date': [date], 'Time': [time], 
                       'L_logged-in': [lichess_stat[0]], 'L_games in progress': [lichess_stat[1]], 'L_ultra bullet': [lichess[L_U_BULLET][PLAYER_COUNT]], 'L_bullet': [lichess[L_BULLET][PLAYER_COUNT]], 'L_blitz': [lichess[L_BLITZ][PLAYER_COUNT]], 'L_rapid': [lichess[L_RAPID][PLAYER_COUNT]], 'L_classical': [lichess[L_CLASSICAL][PLAYER_COUNT]], 'L_chess960': [lichess[L_CHESS960][PLAYER_COUNT]], 
                       'C_total members': [chesscom_stat[0]], 'C_players online': [chesscom_stat[1]], 'C_bullet': [chesscom[C_BULLET][PLAYER_COUNT]], 'C_blitz': [chesscom[C_BLITZ][PLAYER_COUNT]], 'C_rapid': [chesscom[C_RAPID][PLAYER_COUNT]], 'C_daily': [chesscom[C_DAILY][PLAYER_COUNT]], 'C_daily960': [chesscom[C_CHESS960][PLAYER_COUNT]]})
    print(df)
    df.to_csv('scrape_per_hour.csv', mode='a', index=False, header=False)
    print("--- %s seconds ---" % (time.time() - start_time))

def main(): 
    #scrape()
    now = datetime.now()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    sched = BackgroundScheduler()
    sched.add_job(scrape, 'interval', hours=1, next_run_time=next_hour)
    sched.start()

now = datetime.now()
next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
print("The program will run from this time: ", next_hour.strftime("%H:%M"))

main()