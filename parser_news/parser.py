import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.pravda.com.ua/news/'
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.205 Safari/537.36"
}

req = requests.get(url, headers=headers)
src = req.text

with open('Eth/news.html', 'w+', encoding='utf-8') as f:
  f.write(src)

with open('ETH/news.html', 'r', encoding='utf-8') as f:
    src = f.read()

soup = BeautifulSoup(src, 'lxml')

# Збір заголовків, посилань та збереження у json файл
all_news_hrefs = soup.find_all(class_='article_header')

all_news_dict = {}
for item in all_news_hrefs:
   item_title = item.find('a').text
   item_href = 'https://www.pravda.com.ua' + item.find('a')['href']
   all_news_dict[item_title] = item_href

with open('ETH/news.json', 'w+', encoding='utf-8') as f:
   json.dump(all_news_dict, f, indent=4, ensure_ascii=False)

# Збереження файлу json у перемінну
with open('ETH/news_fixed.json', 'r', encoding='utf-8') as f:
    all_news = json.load(f)


for news_title, news_href in all_news.items():

    rep = [',', ' ', '-', '\'', ':', '?', '\\', '/', '*', '"', '<', '>', '|', '\xa0']
    for item in rep:
        if item in news_title:
            news_title = news_title.replace(item, '_')

    req = requests.get(url=news_href, headers=headers)
    src = req.text

    with open(f'ETH/news/{news_title}.html', 'w+', encoding='utf-8') as f:
        f.write(src)

    # Збереження коду сторінки в переміну та пошук потрібних даних
    with open(f'ETH/news/{news_title}.html', 'r', encoding='utf-8') as f:
        src = f.read()

    soup = BeautifulSoup(src, 'lxml')
