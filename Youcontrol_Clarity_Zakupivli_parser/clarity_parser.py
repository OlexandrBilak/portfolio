from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd
import os

# === Налаштування ===
INPUT_FILE = "regional_links_out.xlsx"
OUTPUT_FILE = "regional_links_out.xlsx"


# === Створення драйвера з профілем Chrome ===
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # Створюємо окрему папку для чистого профілю
    profile_path = os.path.abspath("SeleniumProfile")
    options.add_argument(f"--user-data-dir={profile_path}")
    # Не вказуємо --profile-directory, щоб використовувати дефолтний профіль у цій папці

    driver = webdriver.Chrome(service=Service(), options=options)
    return driver



# === Отримання номера телефону по коду ЄДРПОУ ===
def get_phone_number(driver, edrpou):
    try:
        # Відкриваємо сторінку пошуку
        search_url = f"https://clarity-project.info/edrs?query={edrpou}"
        driver.get(search_url)
        time.sleep(2)

        # Знаходимо посилання на сторінку компанії
        profile_link_elem = driver.find_element(By.CSS_SELECTOR, "h5.mb-10 a[href^='/edr/']")
        profile_url = profile_link_elem.get_attribute("href")
        driver.get(profile_url)
        time.sleep(2)

        # Шукаємо елемент з номером телефону
        phone_elem = driver.find_element(By.CSS_SELECTOR, "a[href^='tel:']")
        phone = phone_elem.text.strip()

        print(f"📞 Телефон: {phone}")
        return phone

    except Exception as e:
        print(f"❌ Помилка: {edrpou} — {e}")
        return ""


# === Основна логіка ===
def main(batch_size=None):
    df = pd.read_excel(INPUT_FILE)

    if "Код ЄДРПОУ" not in df.columns:
        print("❌ У файлі немає колонки 'Код ЄДРПОУ'")
        return

    if "Телефон" not in df.columns:
        df["Телефон"] = ""

    driver = create_driver()

    driver.get("https://clarity-project.info/account")
    time.sleep(2)

    if "Увійти" in driver.page_source or "реєстрація" in driver.page_source.lower():
        print("🔐 Будь ласка, увійдіть вручну у відкритому браузері, потім натисніть Enter...")
        input("✅ Натисніть Enter після авторизації в акаунт...")
        driver.get("https://clarity-project.info/account")
        time.sleep(2)

    count = 0
    for idx, row in df.iterrows():
        if batch_size is not None and count >= batch_size:
            break

        edrpou = str(row["Код ЄДРПОУ"]).strip()
        phone_existing = str(row["Телефон"]).strip() if pd.notna(row["Телефон"]) else ""

        if not edrpou or len(edrpou) < 5:
            continue

        if phone_existing != "":
            print(f"⏭️ Пропущено (вже є номер): {edrpou}")
            continue

        print(f"{count}🔍 Обробка: {edrpou}")
        phone = get_phone_number(driver, edrpou)
        df.at[idx, "Телефон"] = phone
        count += 1
        time.sleep(2)


    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ Завершено. Результат збережено у файл: {OUTPUT_FILE}")

    driver.quit()


if __name__ == "__main__":
    # наприклад, обробити лише 10 позицій
    main(batch_size=197)
