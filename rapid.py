from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException as NSEE
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from time import sleep
import pandas as pd

website = 'https://www.chess.com/leaderboard/live/rapid?country=JP&page=1'
path = '/Users/haruk/OneDrive/Desktop/scrape/chromedriver'

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")
# chrome_options.headless = True # also works

driver = webdriver.Chrome(executable_path=path, options=chrome_options)

driver.get(website)
driver.set_window_position(0, 0)
driver.set_window_size(1200, 3000)
ignored_exceptions=(NSEE,StaleElementReferenceException)
#player_name = driver.find_elements("xpath", '//a[@data-test-element="user-tagline-username"]')

def check_exists_by_xpath(xpath):
    try:
        driver.find_element("xpath", xpath)
    except NSEE:
        return False
    return True

try:
    element_present = EC.presence_of_element_located((By.XPATH, '//button[@class="ready-to-play-banner-close"]'))
    WebDriverWait(driver, 20).until(element_present)
except TimeoutException:
    print("Timed out waiting for page to load")

#close ready to play banner
ready_close = driver.find_element("xpath", '//button[@class="ready-to-play-banner-close"]')
ready_close.click()

p_name = []
p_rate = []
p_join = []
p_last = []
#p_stat = []
p_win = []
p_draw = []
p_loss = []

loop = True
page = 1

while (loop):
    print("\nrapid" + str(page) + "\n")
    crash = True
    while(crash):
        try:
            player_data = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((By.XPATH, '//tr[@class="leaderboard-row-show-on-hover"]')))
            crash = False
        except TimeoutException:
            print("Timed out waiting for player data to load")
            driver.refresh()
    for player in player_data:
        #finds element of player name in the table row (tr) and appends it to p_name list
        try:
            name = WebDriverWait(player, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, './td[@class="leaderboard-row-user-cell"]/a/div/a[@data-test-element="user-tagline-username"]'))).text
        except TimeoutException:
            print("Timed out waiting for player name to load")
        p_name.append(name)
        #print(name)# - prints name
        
        #finds element of player rating in the table row (tr) and appends it to p_rate list
        try:
            rate = WebDriverWait(player, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, './td[@class="table-text-right leaderboard-row-score"]/a'))).text
        except TimeoutException:
            print("Timed out waiting for player rating to load")
        p_rate.append(rate)
        #print(rate)

        #finds element of player w/d/l in the table row (tr) and appends it to p_stat list
        try:
            stat = WebDriverWait(player, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, './td[@class="leaderboard-row-rating table-text-right"]/a/span[@class="leaderboard-row-regular-stats leaderboard-row-stats"]'))).text
        except TimeoutException:
            print("Timed out waiting for player stats to load")
        stat = ''.join(stat.split())
        stat_pylist_formatted = stat.split('/')
        #p_stat.append(stat)
        p_win.append(stat_pylist_formatted[0])
        p_draw.append(stat_pylist_formatted[1])
        p_loss.append(stat_pylist_formatted[2])
        #print(stat_pylist_formatted[0] + '/' + stat_pylist_formatted[1] + '/' + stat_pylist_formatted[2])

        #get join date
        #open user popup
        joinloop = True
        while(joinloop):
            try:
                space = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '//div[@class="v5-section-content-slim"]')))
                space.click()
            except TimeoutException:
                print("Timed out waiting for alternate click location to load")
            try:
                profile = WebDriverWait(player, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, './td[@class="leaderboard-row-user-cell"]/a/div/a[@data-test-element="user-tagline-username"]')))
                profile.click()
            except TimeoutException:
                print("Timed out waiting for player profile to load")
            try:
                join = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="user-popover-secondary"]/div[1]'))).text
                joinloop = False
            except TimeoutException:
                print("Timed out waiting for join date to load")
        try:
            join_time_obj = datetime.strptime(join, 'Joined %b %d, %Y')
            join_formed = join_time_obj.strftime('%d-%m-%Y')
        except ValueError:
            if(join == "Joined Just now"):
                join_formed = datetime.today().strftime('%d-%m-%Y')
            else:
                print("fail")
                loop = False
        #print(join_formed)
        p_join.append(join_formed)

        #get last play date
        if (check_exists_by_xpath('//div[@class="user-popover-status"]/div[2]')):
            try:
                last_play = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '//div[@class="user-popover-status"]/div[2]'))).text
                last_play_time_obj = datetime.strptime(last_play, 'Online %b %d, %Y')
                last_play_formed = last_play_time_obj.strftime('%d-%m-%Y')
            except ValueError:
                if(last_play == "Online Just now"):
                    last_play_formed = datetime.today().strftime('%d-%m-%Y')
                else:
                    print("fail")
                    loop = False
        elif (check_exists_by_xpath('//div[@class="user-popover-status"]/div[@class="presence-button-component presence-button-visible"]')):
            last_play_formed = datetime.today().strftime('%d-%m-%Y')
        #print(last_play_formed)
        p_last.append(last_play_formed)

        #click on different area
        try:
            try:
                space = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '//div[@class="v5-section-content-slim"]')))
                space.click()
            except TimeoutException:
                print("Timed out waiting for alternate click location to load")
        except ElementClickInterceptedException:
            try:
                #close ready to play banner
                ready_close = driver.find_element("xpath", '//button[@class="ready-to-play-banner-close"]')
                ready_close.click()
            except NSEE:
                print("click on empty space intercepted by unknown element")
                pass

    #click next page
    try:
        try:
            next_page = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Next Page"]')))
        except TimeoutException:
            print("Timed out waiting for next page button to load")
        if(next_page.is_enabled()):
            next_page.click()
            page+=1
        else:
            print('end')
            loop = False
    except (NSEE,WebDriverException):
        print('\nfail to click on next page due to error\n')
        try:
            #close ready to play banner
            ready_close = driver.find_element("xpath", '//button[@class="ready-to-play-banner-close"]')
            ready_close.click()
        except NSEE:
            pass


driver.quit()

df = pd.DataFrame({'Player name': p_name, 'Rating': p_rate, 'Won': p_win, 'Draw': p_draw, 'Lost': p_loss, 'Last Online': p_last, 'Joined': p_join})
df.to_csv('rapid_leaderboard.csv', index=False)
print(df)
