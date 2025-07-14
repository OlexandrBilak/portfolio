# Ціль: Отримати актуальний курс USD/UAH з сайту банку
import requests
from bs4 import BeautifulSoup
import lxml
import csv

url = 'https://minfin.com.ua/ua/currency/banks/usd/'
headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Mobile Safari/537.36"
}

# req = requests.get(url, headers=headers)
# src = req.text

# with open('Eth/usd_uah/minfin.html', 'w+', encoding='utf-8') as f:
#     f.write(src)

with open('Eth/usd_uah/minfin.html', 'r', encoding='utf-8') as f:
    src = f.read()

soup = BeautifulSoup(src, 'lxml')

all_banks = soup.find('tbody', class_='list').find_all('tr')

with open('Eth/usd_uah/usd_uah.csv', 'w+', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(('Назва банку', 'Курс купівлі', 'Курс продажу'))
    for bank in all_banks:
        bank_name = bank.find('a', class_='mfm-black-link').text.strip()
        bank_buy_price = bank.find('td', class_='responsive-hide mfm-text-right mfm-pr0').text
        bank_sell_price = bank.find('td', class_='responsive-hide mfm-text-left mfm-pl0').text

        if bank_buy_price and bank_sell_price:
            pass
        else:
            bank_buy_price = 'Немає даних'

        print(f'{bank_name} : {bank_buy_price}/{bank_sell_price}')
        writer.writerow((bank_name, bank_buy_price, bank_sell_price))

print('Completed')
