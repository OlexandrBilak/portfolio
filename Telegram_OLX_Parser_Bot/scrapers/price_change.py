
#url = "https://www.olx.ua/d/uk/obyavlenie/apple-iphone-14-pro-max-256gb-deep-purple-neverlock-ideal-IDZB6A9.html"


def price_change(soup, url):
    
    try:
        price = soup.find('h3', class_="css-yauxmy").text
    except:
        pass

    return price


def price_change(soup, url):
    data = []

    try:
        title = soup.find('h4', class_='css-1au435n').text
        price = soup.find('h3', class_="css-yauxmy").text
        link = url
    except:
        pass

    if link not in data:
        data.append(
            {
                'title': title,
                'price': price,
                'link': link
            }
        )
    
    return data

