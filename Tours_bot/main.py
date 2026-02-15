import urllib.parse
import asyncio
import json
import os
import hashlib
import logging
import random
import time
from bs4 import BeautifulSoup

import gspread
from google.oauth2.service_account import Credentials
from telegram import Bot, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from urllib.parse import urlparse

from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# LOGGING 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("tour_bot")
logger.info("=== BOT STARTED ===")


# Налаштування


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS_FILE = "###"
SPREADSHEET_ID = "###"
STATE_FILE = "state.json"
USER_FILE = "user.json"

STATUS_COLUMN_NAME = "status"
TARGET_STATUSES = ["AWAIT", "await"]
NEW_STATUS = "SENT"

BOT_TOKEN = "####"

# Google Sheets

creds = Credentials.from_service_account_file(
    CREDENTIALS_FILE,
    scopes=SCOPES
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# Telegram

bot = Bot(token=BOT_TOKEN)

# STATE

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"processed": {}}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def row_hash(row: dict) -> str:
    raw = "|".join(str(v) for v in row.values())
    return hashlib.md5(raw.encode()).hexdigest()

# USER

def load_user():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f).get("chat_id")
    return None

def save_user(chat_id):
    with open(USER_FILE, "w") as f:
        json.dump({"chat_id": chat_id}, f)

# SELENIUM BOOKING

def trim_description(text: str, min_len=100, max_len=400) -> str:
    if len(text) <= max_len:
        return text
    cut = text[:max_len]
    dot = cut.rfind(".")
    if dot != -1 and dot > min_len:
        return cut[:dot + 1]
    return cut


def is_valid_hotel_photo(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    if "cf.bstatic.com" not in parsed.netloc:
        return False
    if "/xdata/images/hotel/" not in parsed.path:
        return False
    if not parsed.path.lower().endswith((".jpg", ".jpeg")):
        return False
    blacklist = ["design-assets","images-flags","icon","logo","avatar","square60","square90"]
    return not any(bad in parsed.path for bad in blacklist)

def build_search_url(hotel_name: str) -> str:
    query = urllib.parse.quote(hotel_name)
    return f"https://www.booking.com/searchresults.uk.html?ss={query}"

def get_first_hotel_link(driver, search_url: str):
    driver.get(search_url)
    wait = WebDriverWait(driver, 20)
    try:
        first_link = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="title-link"]'))
        )
        href = first_link.get_attribute("href")
        logger.info(f"Знайдено перший готель: {href}")
        return href.split("?")[0]
    except Exception as e:
        logger.error(f"Не знайдено готель: {e}")
        return None

def get_hotel_photos(driver, hotel_url: str, limit: int = 6):
    try:
        driver.get(hotel_url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        photos = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and is_valid_hotel_photo(src):
                photos.append(src)
            if len(photos) >= limit:
                break
            
        logger.info(f"Знайдено фото: {src}")
        return photos
    except Exception as e:
        logger.error(f"Не вдалося отримати фото: {e}")
        return []

def get_hotel_facilities(driver, hotel_url: str, limit: int = 6):
    driver.get(hotel_url)
    wait = WebDriverWait(driver, 20)
    try:
        block = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'p[data-testid="property-description"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", block)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        about = soup.select_one('p[data-testid="property-description"]').text.strip()
        description = trim_description(about)
        if not description:
            return []
        logger.info(f"Опис готелю: {description}")
        return description
    except Exception as e:
        logger.error(f"Не вдалося отримати зручності: {e}")
        return []

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

# ВІДПРАВКА ТУРУ

async def send_tour(row: dict, driver, chat_id):
    try:
        hotel_name = row.get("отель", "")
        photos = []
        facilities = []

        if hotel_name:
            search_url = build_search_url(hotel_name)
            hotel_url = get_first_hotel_link(driver, search_url)
            if hotel_url:
                photos = get_hotel_photos(driver, hotel_url)
                facilities = get_hotel_facilities(driver, hotel_url)

        message = f"""
⭐️ <a href="{row.get('посилання','')}">{row.get('отель','')}</a>
📍 {row.get('країна','')}

{facilities}

📅 {row.get('дата','')} • {row.get('ночей','')} ночей
✈️ Виліт з: {row.get('виліт','')}
👤 Туристів: {row.get('туристів','')}
🍽 Харчування: {row.get('харчування','')}
💰 Ціна: {row.get('ціна','')}

✅У вартість туру входить:
-прямий переліт
-проживання
-харчування
-трансфер

📞 За детальною інформацією та прорахунком інших варіантів звертайтеся:

☎️ <a href="https://wa.me/###">Написати у WhatsApp</a> +####
☎️ +###
☎️ Консультація з менеджером: @###

#{row.get('країна','')}
"""

        if photos:
            media_group = []
            for idx, url in enumerate(photos[:6]):
                if idx == 0:
                    media_group.append(InputMediaPhoto(media=url, caption=message, parse_mode="HTML"))
                else:
                    media_group.append(InputMediaPhoto(media=url))
            await bot.send_media_group(chat_id=chat_id, media=media_group)
        else:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Помилка send_tour: {e}", exc_info=True)

# ОСНОВНИЙ ЦИКЛ

async def main_loop():
    state = load_state()
    chat_id = load_user()
    if not chat_id:
        logger.error("Немає chat_id користувача. Спершу потрібно запустити бота командою /start")
        return

    driver = create_driver()

    try:
        while True:
            rows = sheet.get_all_values()

            if len(rows) < 2:
                await asyncio.sleep(3)
                continue

            headers = rows[0]
            status_index = headers.index(STATUS_COLUMN_NAME) + 1

            for idx, row_values in enumerate(rows[1:], start=2):
                row = dict(zip(headers, row_values))
                status = row.get(STATUS_COLUMN_NAME, "").strip().upper()

                if status == "AWAIT":
                    await send_tour(row, driver, chat_id)
                    sheet.update_cell(idx, status_index, "SENT")

            await asyncio.sleep(3)


    finally:
        driver.quit()

# /start handler для отримання chat_id

async def start(update, context):
    chat_id = update.effective_chat.id
    save_user(chat_id)
    await context.bot.send_message(chat_id=chat_id, text="Вітаю! Тепер ти отримуватимеш тури від бота.")

# START BOT

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    asyncio.get_event_loop().create_task(main_loop())
    app.run_polling()
