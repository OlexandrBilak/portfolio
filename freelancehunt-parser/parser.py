import bs4
import requests, lxml
from bs4 import BeautifulSoup
import time, os
from requests import options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# ---------------- CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
profile_path = os.path.join(BASE_DIR, "selenium_profile")  # папка для профілю
url = 'https://freelancehunt.com/projects/skill/parsing-danih/169.html'
lists = []
SEEN_FILE = "seen_lists.txt"

# Дані Telegram
TELEGRAM_BOT_TOKEN = "8372299801:AAG9peGK4qFbN9R5hxF2lPa_Em4guYOVUfo"
TELEGRAM_CHAT_ID = "731681925"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

CHECK_INTERVAL = 1800  # 30 хв = 1800 секунд
# ----------------------------------------


def load_seen(): # Завантажуємо всі вже збережені оголошення
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


def save_seen(href): # Дописуємо нове посилання у файл
    with open(SEEN_FILE, "a") as f:
        f.write(href + "\n")


def send_telegram_message(title, href): # Надсилає повідомлення у Telegram"
    text = f"🆕 <b>{title}</b>\n{href}"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(TELEGRAM_API_URL, data=payload)


def get_driver(): # Запуск та налаштування Chrome
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    return driver


def parser_new_lists(driver): # Парсинг сайту
    seen = load_seen()
    soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
    blok_list = soup.find("tbody").find_all("tr")

    for list in blok_list:
        href = list.find("a").get("href")
        title = list.find("a").text.strip()

        if href in seen:
            continue

        lists.append([href, title])
        print('Знайдено оголошення:', href)
        save_seen(href)
        send_telegram_message(title, href)


def main(): # Основна логіка
    while True:
        try:
            driver = get_driver()
            driver.get(url)

            print('Парсер запущено')
            parser_new_lists(driver)
            time.sleep(10)

            driver.quit()
        except Exception as e:
            print("❌ Помилка:", e)

        print(f"⏳ Чекаємо {CHECK_INTERVAL / 60} хв...")
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
