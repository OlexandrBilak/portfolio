
#url = "https://www.olx.ua/uk/rabota/"


def get_vacancie(soup, url):
    data = []

    all_vacancies = soup.find_all("div", class_='css-5ae0t9')

    for vac in all_vacancies:

        try:
            title = vac.find('h4', class_='css-18xq10d').text
            price_tag = vac.find('p', class_='css-p0ppl7')
            price = price_tag.text.strip() if price_tag else 'Ціна не вказана'
            link = f"https://www.olx.ua{vac.find('a', class_='css-13gxtrp').get('href')}"
        except:
            continue

        if link not in data:
            data.append(
                {
                    'title': title,
                    'price': price,
                    'link': link
                }
            )

    return data

