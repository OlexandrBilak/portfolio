#url = "https://www.olx.ua/uk/elektronika/telefony-i-aksesuary/"


def new_listings(soup, url):
    data = []

    all_listings = soup.find_all("div", class_='css-1r93q13')

    for lists in all_listings:
        try:
            title = lists.find('h4', class_='css-hzlye5').text
            price = lists.find('p', class_='css-blr5zl').text
            link = f"https://www.olx.ua{lists.find('a', class_='css-1tqlkj0').get('href')}"
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

