import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

COOKIES = {
    "spm1": "acaeda354e245698578f871123c47f3f",
    "yc_search_addon_shows": "785917736121dbba8269b12c48fb76a3a4feba8e55db632ef9f029f06339a62ba%3A2%3A%7Bi%3A0%3Bs%3A21%3A%22yc_search_addon_shows%22%3Bi%3A1%3Bi%3A4%3B%7D%3A2%3A%7Bi%3A0%3Bs%3A21%3A%22yc_search_addon_shows%22%3Bi%3A1%3Bi%3A4%3B%7D",
    "_csrf-frontend":"1556aadb15bd6408b7cae009e1662930eb5fa6170cea8318fb0638acc445d0f2a%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22_csrf-frontend%22%3Bi%3A1%3Bs%3A32%3A%22_4PD9bKSisnLWlQlEShyQ8DwzCcRSh2Y%22%3B%7D",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}

SEARCH_TERMS = [
    "військова",
    "військова адміністрація",
    "обласна державна адміністрація",
    "міська рада",
    "територіальна громада"]

BASE_URL = "https://youcontrol.com.ua"
results = []

REGIONS = {
    15: "Миколаївська область",
    16: "Одеська область",
    17: "Полтавська область",
    18: "Рівненська область",
    20: "Сумська область",
    21: "Тернопільська область",
    22: "Харківська область",
    23: "Херсонська область",
    24: "Хмельницька область",
    25: "Черкаська область",
    27: "Чернігівська область",
    26: "Чернівецька область",
    19: "Севастополь",
    1: "Автономна Республіка Крим"
}

def parse_all_companies():
    for region_code, region_name in REGIONS.items():
        for item in SEARCH_TERMS:
            page = 1
            last_page = 1
            url = f"{BASE_URL}/search/?country=1&q={item}&r%5B%5D={region_code}&s%5B0%5D=1&e=1&t=0&page={page}"
            req = requests.get(url=url, headers=HEADERS, cookies=COOKIES)
            soup = BeautifulSoup(req.text, "lxml")

            pagination = soup.find("ul", class_="pagination")
            if pagination:
                page_items = pagination.find_all("li")
                numbers = [int(li.text) for li in page_items if li.text.isdigit()]
                if numbers:
                    last_page = max(numbers)

            while page <= last_page:
                print(f"📄 {region_name} | Сторінка {page} | Запит '{item}'")
                url = f"{BASE_URL}/search/?country=1&q={item}&r%5B%5D={region_code}&s%5B0%5D=1&e=1&t=0&page={page}"
                req = requests.get(url=url, headers=HEADERS, cookies=COOKIES)
                soup = BeautifulSoup(req.text, "lxml")

                try:
                    all_companies = soup.find_all('div', class_='name-org')
                    for company in all_companies:
                        try:
                            href = company.find('a').get('href')
                            name = company.text.strip()
                            if item.lower() in name.lower():
                                results.append({
                                    "Регіон": region_name,
                                    "Назва": name,
                                    "URL": BASE_URL + href
                                })
                        except:
                            continue
                except:
                    pass

                page += 1
                time.sleep(1)

parse_all_companies()
df = pd.DataFrame(results)
df.to_excel("regional_links2.xlsx", index=False)
print("✅ Збережено у regional_links2.xlsx")
