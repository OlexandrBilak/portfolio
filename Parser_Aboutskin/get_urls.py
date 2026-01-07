import requests
from bs4 import BeautifulSoup

cookies = {
    '_ga': 'GA1.1.85573617.1766952688',
    'cmplz_consented_services': '',
    'cmplz_policy_id': '35',
    'cmplz_marketing': 'allow',
    'cmplz_statistics': 'allow',
    'cmplz_preferences': 'allow',
    'cmplz_functional': 'allow',
    'cmplz_banner-status': 'dismissed',
    'woodmart_recently_viewed_products': '20721|20973|15271|10826|21431|20711|21414|21447',
    'shop_per_page': '24',
    '_ga_2W05T9XS06': 'GS2.1.s1767031179$o4$g1$t1767031298$j28$l0$h101830602',
}
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'uk,ru;q=0.9,en-US;q=0.8,en;q=0.7,pl;q=0.6,fr;q=0.5,de;q=0.4',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://aboutskin.com.ua/',
    'sec-ch-ua': '"Opera";v="125", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 OPR/125.0.0.0',
    # 'cookie': '_ga=GA1.1.85573617.1766952688; cmplz_consented_services=; cmplz_policy_id=35; cmplz_marketing=allow; cmplz_statistics=allow; cmplz_preferences=allow; cmplz_functional=allow; cmplz_banner-status=dismissed; woodmart_recently_viewed_products=20721|20973|15271|10826|21431|20711|21414|21447; shop_per_page=24; _ga_2W05T9XS06=GS2.1.s1767031179$o4$g1$t1767031298$j28$l0$h101830602',
}

def get_categories():
    with open('categories/type_skin.txt', 'r', encoding='utf-8') as f:
        urls = [u.strip() for u in f if u.strip()]

    for base_url in urls:
        page = 1

        while True:
            page_url = f"{base_url}page/{page}/"

            r = requests.get(page_url, headers=headers, cookies=cookies)

            # якщо сторінка не існує
            if r.status_code != 200:
                break

            soup = BeautifulSoup(r.text, "lxml")

            # якщо товарів немає — стоп
            if not soup.find(
                'div',
                class_="products wd-products wd-grid-g grid-columns-4 elements-grid wd-quantity-enabled pagination-pagination wd-stretch-cont-lg wd-stretch-cont-md wd-stretch-cont-sm wd-products-with-bg"
            ).find_all('div', class_='product-element-top wd-quick-shop'):
                break

            print(page_url)
            page += 1


def main():
    get_categories()


if __name__ == '__main__':
    main()
