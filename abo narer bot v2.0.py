# Modules
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementNotInteractableException
from time import sleep
from pyautogui import press, hotkey
from os import chdir, path, mkdir, rename
# ------------------------------------------------------------------------------------------ #
def get_range(range):

    if range == ['']:
        start = 1
        end = None
    else:
       start = range[0] if range[0] != '' else 1
       end = range[-1] if range[-1] != '' else None
    
    return int(start), end
# ------------------------------------------------------------------------------------------ #

# Input Data
series = input("Series: ").strip().title()
season = input("Season: ").strip().split('-')
episode = input("Episodes: ").strip().split('-')

file_name = None
size = 0

s_start = get_range(season)[0]
s_end = get_range(season)[1]

e_start = get_range(episode)[0]
e_end = get_range(episode)[1]



# ------------------------------------------------------------------------------------------ #

# Change current working directory 
chdir(path.dirname(path.abspath(__file__)))

# setup chrome options
options = Options()
options.add_argument("--disable-notifications")

# open browser
browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
browser.maximize_window()
browser.implicitly_wait(15)

# ------------------------------------------------------------------------------------------ #

# -- Functions -- #

def get_size_mb(size):

    size = size[1:-1] if size[0] == '(' else size

    size = float(size[:-2]) * 1024 if size[-2] == 'G' else float(size[:-2])

    return size

def get_size(size):

    if size < 1024:
        size = round(size, 2)
        size = f"{size}MB"
    else:
        size = size / 1024
        size = round(size, 2)
        size = f"{size}GB"
    
    return size

def get_download_link(file_name):

    global size

    btn1 = browser.find_element_by_xpath('//*[@id="watch_dl"]/table/tbody/tr[1]/td[4]/a[1]')
    btn1.click()

    browser.switch_to.window(browser.window_handles[1])

    btn2 = browser.find_element_by_xpath('/html/body/div[1]/div/p/a[1]')

    if btn2.get_attribute('href') == None:

        btn2.click()
        browser.switch_to.window(browser.window_handles[1])
        sleep(2)
        browser.refresh()

    btn3 = browser.find_element_by_xpath('/html/body/div[1]/div/p/a[1]') 
    download_link = btn3.get_attribute('href')

    size_span = browser.find_element_by_xpath('/html/body/div[1]/div/span').text

    size += get_size_mb(size_span)

    for _ in range(len(browser.window_handles) - 1):
        hotkey('ctrl', 'w')
        sleep(0.5)

    browser.switch_to.window(browser.window_handles[0])

    if not path.isdir(series):
        mkdir(series)
    
    links_file = open(series + r"/" + file_name, 'a')
    links_file.write(f"{download_link}\n")
    links_file.close()

    

def get_all_links(e_start, e_end):

    episodes = browser.find_element_by_xpath('//*[@id="mainLoad"]/div[3]/div[2]').find_elements_by_tag_name('a')
    episodes_num = len(episodes)
    episodes.reverse()
    episodes[e_start - 1].click()

    get_download_link(file_name)

    sleep(1)

    if e_end == None:
        e_end = episodes_num

    for i in range(e_start, int(e_end)):
        episodes = browser.find_element_by_xpath('//*[@id="mainLoad"]/div[6]/div[2]').find_elements_by_tag_name('a')
        episodes.reverse()
        episodes[i].click()

        sleep(3)

        get_download_link(file_name)

def sending_file(file_path, login):

    hotkey('ctrl', 't')
    browser.get("https://www.facebook.com/messages/t/100005178106513")
    hotkey('ctrl', 'w')
    browser.switch_to.window(browser.window_handles[0])

    if login:
        email = browser.find_element_by_xpath('//*[@id="email"]')
        passw = browser.find_element_by_xpath('//*[@id="pass"]')
        login = browser.find_element_by_xpath('//*[@id="loginbutton"]')

        email.send_keys("mohamedhazem421@ymail.com")
        passw.send_keys("mohamedfcb10")
        login.click()

    sleep(1)

    browser.switch_to.window(browser.window_handles[0])

    send_file = browser.find_elements_by_name('attachment[]')[1]
    send_file.send_keys(file_path)
    press('enter')
    sleep(4)


# ------------------------------------------------------------------------------------------ #

# Main step
browser.get("https://dear.egybest.me/")

search_bar = browser.find_element_by_xpath('//*[@id="head"]/div/div[2]/form/input[2]')
search_bar.send_keys(series)

sleep(1)
press('down')
sleep(0.5)
press('down')
press('enter')

sleep(1)
hotkey('ctrl', 'w')

seasons = browser.find_element_by_xpath('//*[@id="mainLoad"]/div[2]/div[2]/div').find_elements_by_tag_name('a')
seasons.reverse()
seasons_num = len(seasons)

if s_end == None:
    s_end = seasons_num

# -------------------------------------------------------------------------------------------------------------------------- #

# Loop 
for current_season in range(s_start - 1, int(s_end)):

    # Go to season page
    try:
        seasons[current_season].click()
    except ElementNotInteractableException: 
        browser.execute_script("arguments[0].click()", seasons[current_season])

    # define file name & path
    file_name = f"{series}-S{str(current_season + 1).zfill(2)}.txt"
    file_path = path.dirname(path.abspath(__file__)) + r"/" + series + r"/" + file_name

    sleep(1)

    # get all episodes links
    get_all_links(e_start, e_end)

    e_start = 1
    e_end = None

    sleep(3)

    # Type size in file name
    size = get_size(size)

    new_file_name = f"{series}-S{str(current_season + 1).zfill(2)}-{size}.txt"
    new_file_path = path.dirname(path.abspath(__file__)) + r"/" + series + r"/" + new_file_name

    rename(file_path, new_file_path)

    # size = 0 for next season
    size = 0

    # check to login or not
    if current_season == s_start - 1:
        login = True
    else:
        login = False

    # sending file via facebook
    sending_file(new_file_path, login)

    # exit in last season
    if current_season == int(s_end) - 1:
        browser.quit()
        exit()

    # return to main step state
    hotkey('ctrl', 't')
    browser.get("https://dear.egybest.me/")
    sleep(0.5)
    hotkey('ctrl', 'w')
    
    browser.switch_to.window(browser.window_handles[0])
    
    sleep(10)

    search_bar = browser.find_element_by_xpath('//*[@id="head"]/div/div[2]/form/input[2]')
    search_bar.send_keys(series)

    sleep(1)
    press('down')
    sleep(0.5)
    press('down')
    press('enter')

    sleep(1)
    hotkey('ctrl', 'w')

    seasons = browser.find_element_by_xpath('//*[@id="mainLoad"]/div[2]/div[2]/div').find_elements_by_tag_name('a')
    seasons.reverse()

    sleep(1)