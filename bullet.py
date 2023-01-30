from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException as NSEE
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from time import sleep
import pandas as pd

website = 'https://www.chess.com/leaderboard/live/bullet?country=JP&page=1'
path = '/Users/haruk/OneDrive/Desktop/scrape/chromedriver'

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")
# chrome_options.headless = True # also works

driver = webdriver.Chrome(executable_path=path, options=chrome_options)

driver.get(website)
driver.set_window_position(0, 0)
driver.set_window_size(1440, 900)
ignored_exceptions=(NSEE,StaleElementReferenceException)
#player_name = driver.find_elements("xpath", '//a[@data-test-element="user-tagline-username"]')

try:
    element_present = EC.presence_of_element_located((By.XPATH, '//button[@class="ready-to-play-banner-close"]'))
    WebDriverWait(driver, 20).until(element_present)
except TimeoutException:
    print("Timed out waiting for page to load")

#close ready to play banner
ready_close = driver.find_element("xpath", '//button[@class="ready-to-play-banner-close"]')
ready_close.click()

p_name = []

loop = True
page = 1

while (loop):
    print("\nbullet" + str(page) + "\n")
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

df = pd.DataFrame({'Player name': p_name})
df.to_csv('bullet_leaderboard.csv', index=False)
print(df)
