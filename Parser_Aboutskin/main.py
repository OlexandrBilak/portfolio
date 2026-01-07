import requests
import pandas as pd
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
products = []

CATEGORY_MAP = {
    "oily-skin": "Жирна",
    "combined-skin": "Комбінована",
    "normal-skin": "Нормальна",
    "problem-skin": "Проблемна",
    "dry-skin-type-skin": "Суха",
    "sensitive-skin": "Чутлива",
}




def get_pages():
    for page in range(1, 27):
        url = f"https://aboutskin.com.ua/shop/page/{page}/?per_page=24"
        response = requests.get(url, headers=headers, cookies=cookies)

        with open(f"pages/page-{page}.html", 'w+') as f:
            f.write(response.text)

        print(f"[INFO] Збережено сторінку {page}.")


def get_items():
    for page in range(1, 27):
        with open(f"pages/page-{page}.html", 'r+') as f:
            soup = BeautifulSoup(f, 'lxml')
            try:
                all_items = soup.find('div', class_="products wd-products wd-grid-g grid-columns-4 elements-grid wd-quantity-enabled pagination-pagination wd-stretch-cont-lg wd-stretch-cont-md wd-stretch-cont-sm wd-products-with-bg").find_all('div', class_='product-element-top wd-quick-shop')
                for item in all_items:
                    items = item.find('a').get('href')
                    with open("all_items_urls.txt", 'a+') as f:
                        f.write(f"{items}\n")
            except Exception:
                continue


def get_data():
    with open("all_items_urls.txt", 'r+') as f:
        all_items = f.readlines()

        for item in all_items:
            print(f'[INFO] Збір даних з: {item}')

            response = requests.get(item, headers=headers, cookies=cookies)
            soup = BeautifulSoup(response.text, 'lxml')

            item_url = normalize_url(item)
            print(item_url)

            try:
                categories = soup.find('nav', class_='wd-breadcrumbs woocommerce-breadcrumb').find_all('a')
                category_all = [category.text.strip() for category in categories]
                print(category_all, len(category_all))
                category = ''
                subcategory = ''
                category = category_all[1:-1]
                subcategory = category_all[-1]

            except Exception:
                category = ' '
                subcategory = ' '
            print(category)
            print(subcategory)

            try:
                title = soup.find('h1', class_='product_title entry-title wd-entities-title').text.strip()
            except Exception:
                title = ''
            print(title)

            try:
                short_descritption_html = soup.find('div', class_='woocommerce-product-details__short-description')
                short_descritption = short_descritption_html.text.strip()
            except Exception:
                short_descritption_html = ''
                short_descritption = ''
            print(short_descritption_html)
            print(short_descritption)

            try:
                full_description_html = soup.find('div', class_='woocommerce-Tabs-panel panel entry-content wc-tab woocommerce-Tabs-panel--description')
                full_description = full_description_html.text.strip()
            except Exception:
                full_description_html = ''
                full_description = ''
            print(full_description_html)
            print(full_description)

            try:
                price = soup.find('p', class_='price').find('span', class_='woocommerce-Price-amount amount').text.strip().split()[0]
                currency = soup.find('p', class_='price').find('span', class_='woocommerce-Price-amount amount').text.strip().split()[1]
                amount = soup.find('p', class_='price').find('span', class_='wd-price-unit').text.strip()
            except Exception:
                price = ''
                currency = ''
                amount = ''
            print(price)
            print(currency)
            print(amount)

            try:
                brand = soup.find('td', class_='woocommerce-product-attributes-item__value').text.strip()
            except Exception:
                brand = ''
            print(brand)

            try:
                article = soup.find('div', class_='product_meta wd-layout-inline').find('span', class_='sku').text.strip()
            except Exception:
                article = ''
            print(article)

            try:
                compound = soup.find('div', class_='woocommerce-Tabs-panel panel entry-content wc-tab woocommerce-Tabs-panel--wd_custom_tab').text.strip()
            except Exception:
                compound = ''
            print(compound)

            try:
                img_url = soup.find('figure').find('a').get('href')
            except Exception:
                img_url = ''
            print(img_url)

            product = {
                "item_url": item_url,
                "category": " > ".join(category) if isinstance(category, list) else category,
                "subcategory": subcategory,
                "title": title,
                "short_description_html": str(short_descritption_html),
                "short_descriptions_text": short_descritption,
                "full_description_html": str(full_description_html),
                "full_description_text": full_description,
                "price": price,
                "currency": currency,
                "amount": amount,
                "brand": brand,
                "article": article,
                "compound": compound,
                "img_url": img_url
            }

            products.append(product)

        df = pd.DataFrame(products)
        df.to_excel("aboutskin_products.xlsx", index=False)
        print(f"[OK] Збережено {len(df)} товарів у aboutskin_products.xlsx")


def get_skin_problem_from_url(url):
    for slug, name in CATEGORY_MAP.items():
        if f"/{slug}/" in url:
            return name
    return ""


def normalize_url(url):
    return url.strip().split("?")[0].rstrip("/")



def get_categories():
    # читаємо xlsx
    df = pd.read_excel("aboutskin_products.xlsx", dtype=str).fillna("")

    # якщо колонки ще немає — створюємо
    if "type-skin" not in df.columns:
        df["type-skin"] = ""

    # lookup: url → index
    url_to_index = {
        normalize_url(url): i
        for i, url in enumerate(df["item_url"])
        if url
    }

    with open('categories/type_skin.txt', 'r', encoding='utf-8') as f:
        urls = [u.strip() for u in f if u.strip()]

    for page_url in urls:
        skin_problem = get_skin_problem_from_url(page_url)
        if not skin_problem:
            continue

        print(f"[INFO] Категорія: {skin_problem} | {page_url}")

        r = requests.get(page_url, headers=headers, cookies=cookies)
        if r.status_code != 200:
            continue

        soup = BeautifulSoup(r.text, "lxml")

        try:
            products = soup.find(
                'div',
                class_="products wd-products wd-grid-g grid-columns-4 elements-grid wd-quantity-enabled pagination-pagination wd-stretch-cont-lg wd-stretch-cont-md wd-stretch-cont-sm wd-products-with-bg"
            ).find_all('div', class_='product-element-top wd-quick-shop')
        except Exception:
            continue

        for product in products:
            a = product.find('a')
            if not a:
                continue

            product_url = normalize_url(a.get('href'))
            print(product_url)

            # якщо товар є в XLSX
            if product_url in url_to_index:
                idx = url_to_index[product_url]
                df.at[idx, "type-skin"] = skin_problem
                print(f"[OK] Оновлено: {product_url}")
            else:
                print(f"[MISS] {product_url}")

    # зберігаємо результат
    df.to_excel("aboutskin_products.xlsx", index=False)
    print("[OK] type-skin успішно оновлено")


def mark_testers():
    # читаємо xlsx
    df = pd.read_excel("aboutskin_products.xlsx", dtype=str).fillna("")

    # якщо колонки ще немає — створюємо
    if "is_tester" not in df.columns:
        df["is_tester"] = ""

    # створюємо lookup: url → index
    url_to_index = {
        normalize_url(url): i
        for i, url in enumerate(df["item_url"])
        if url
    }

    # читаємо список тестерів
    with open('categories/testers.txt', 'r', encoding='utf-8') as f:
        tester_urls = [normalize_url(u.strip()) for u in f if u.strip()]

    # проходимо по кожному URL і ставимо 'yes'
    for tester_url in tester_urls:
        if tester_url in url_to_index:
            idx = url_to_index[tester_url]
            df.at[idx, "is_tester"] = "yes"
            print(f"[OK] Оновлено: {tester_url}")
        else:
            print(f"[MISS] {tester_url}")

    # зберігаємо результат
    df.to_excel("aboutskin_products.xlsx", index=False)
    print("[OK] is_tester успішно оновлено")


def mark_instock():
    # читаємо xlsx
    df = pd.read_excel("aboutskin_products_updated.xlsx", dtype=str).fillna("")

    # якщо колонки ще немає — створюємо
    if "is_instock" not in df.columns:
        df["is_instock"] = ""

    # lookup: url → index
    url_to_index = {
        normalize_url(url): i
        for i, url in enumerate(df["item_url"])
        if url
    }

    page = 1
    updated = 0

    while True:
        page_url = f"https://aboutskin.com.ua/shop/page/{page}/?stock_status=instock"
        print(f"[INFO] Перевіряємо: {page_url}")

        r = requests.get(page_url, headers=headers, cookies=cookies)
        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.text, "lxml")

        try:
            product_blocks = soup.find(
                "div",
                class_="products wd-products wd-grid-g grid-columns-4 elements-grid wd-quantity-enabled pagination-pagination wd-stretch-cont-lg wd-stretch-cont-md wd-stretch-cont-sm wd-products-with-bg"
            ).find_all("div", class_="product-element-top wd-quick-shop")
        except Exception:
            break

        # якщо сторінка порожня — стоп
        if not product_blocks:
            print("[STOP] Товарів більше немає")
            break

        for product in product_blocks:
            a = product.find("a")
            if not a:
                continue

            product_url = normalize_url(a.get("href"))

            if product_url in url_to_index:
                idx = url_to_index[product_url]
                df.at[idx, "is_instock"] = "yes"
                updated += 1
                print(f"[OK] In stock: {product_url}")
            else:
                print(f"[MISS] {product_url}")

        page += 1

    df.to_excel("aboutskin_products_updated.xlsx", index=False)
    print(f"[DONE] is_instock оновлено для {updated} товарів")



def main():
    # get_pages()
    #get_items()
    #get_data()
    #get_categories()
    #mark_testers()
    mark_instock()


if __name__ == '__main__':
    main()
