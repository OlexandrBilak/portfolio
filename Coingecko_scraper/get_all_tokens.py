import requests
import openpyxl
from bs4 import BeautifulSoup
from openpyxl import Workbook
import os
import json
from datetime import datetime

FILENAME = 'coingecko.xlsx'


def create_table():
    if os.path.exists(FILENAME):
        return

    wb = Workbook()
    ws = wb.active
    ws.append([
        "created_at_utc",
        "case_source",
        "token_name",
        "token_symbol",
        "volume_24h",
        "volatility_24h",
        "token_chain",
        "token_contract",
        "token_link",
        "company_name",
        "company_website",
        "company_socials",
        "company_twitter",
        "company_telegram",
        "listings_count",
        "CEX_count",
        "DEX_count",
        "tags"
    ])
    wb.save(FILENAME)


def get_all_tokens(ws):
    FILE_PATH = '4.html'  # HTML文件路径
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')

    all_tokens = soup.find('tbody').find_all('tr')

    for token in all_tokens:
        try:
            created_at_utc = datetime.utcnow().isoformat()
            case_source = 'CASE4'

            token_names = token.find(
                'div',
                class_='tw-text-gray-700 dark:tw-text-moon-100 tw-font-semibold tw-text-sm tw-leading-5'
            ).text.strip()
            #print(token_names)


            token_name = token_names.split('\n')[0]
            token_symbol = token_names.split('\n')[-1]
            print(token_name, token_symbol)

            tds = token.find_all("td")

            volume_24h = round(float(tds[7]["data-sort"]), 1)
            print(volume_24h)

            change_span = token.find(
                "span",
                attrs={"data-attr": "price_change_percentage_24h"}
            )
            volatility_24h = round(
                float(json.loads(change_span["data-json"])["usd"]), 1
            )
            print(volatility_24h)

            token_link = token.find('a').get('href')
            print(token_link)

            # поки немає — залишаємо None
            token_chain = None
            token_contract = None
            company_name = None
            company_website = None
            company_socials = None
            company_twitter = None
            company_telegram = None
            listings_count = None
            CEX_count = None
            DEX_count = None
            tags = None

            ws.append([
                created_at_utc,
                case_source,
                token_name,
                token_symbol,
                volume_24h,
                volatility_24h,
                token_chain,
                token_contract,
                token_link,
                company_name,
                company_website,
                company_socials,
                company_twitter,
                company_telegram,
                listings_count,
                CEX_count,
                DEX_count,
                tags
            ])

            print(f"SAVED: {token_name} ({token_symbol})")

        except Exception as e:
            print("SKIP ROW:", e)


def main():
    create_table()
    wb = openpyxl.load_workbook(FILENAME)
    ws = wb.active

    get_all_tokens(ws)

    wb.save(FILENAME)
    print("DONE")


if __name__ == '__main__':
    main()
