from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import os
from bs4 import BeautifulSoup
import csv
import unicodedata


def clean_price(price):
    cleaned = unicodedata.normalize("NFKD", price)
    return cleaned.replace('\xa0', ' ').replace('₴', '').strip()


# options = Options()
#
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver.maximize_window()
#
# url = 'https://rozetka.com.ua/ua/mobile-phones/c80003/'
# driver.get(url)
#
# time.sleep(random.uniform(4, 7))
#
# scroll_pause_time = 1
# last_height = driver.execute_script("return document.body.scrollHeight")
#
# while True:
#     driver.execute_script("window.scrollBy(0, 400);")
#     time.sleep(scroll_pause_time)
#     new_height = driver.execute_script("return window.pageYOffset + window.innerHeight")
#     if new_height >= last_height:
#         break
#
# time.sleep(random.uniform(3, 5))
#
# html = driver.page_source
# driver.quit()
# os.makedirs('Eth/rozetka_phones', exist_ok=True)

with open('Eth/rozetka_phones/rozetka_phones.html', 'r', encoding='utf-8') as f:
    src = f.read()

soup = BeautifulSoup(src, 'lxml')

# Назва товару, Ціна, Посилання на товар, Наявність (є/немає)
all_phones = soup.find_all('div', class_='content')

with open('Eth/rozetka_phones/rozetka_phones.csv', 'w+', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(('Назва товару', 'Ціна', 'Посилання на товар', 'Наявність'))

    for phone in all_phones:
        phone_text = phone.find('img').get('alt')
        phone_price_1 = phone.find('div', class_='price').text
        phone_price = clean_price(phone_price_1)
        phone_href = phone.find('a').get('href')
        phone_sell_status = phone.find('rz-tile-sell-status').text.strip()
        phone_list = (
            phone_text,
            phone_price,
            phone_href,
            phone_sell_status
        )
        writer.writerow(phone_list)
