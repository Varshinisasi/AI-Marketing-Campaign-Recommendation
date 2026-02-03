import requests
from bs4 import BeautifulSoup

def generic_scrape(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    products = []

    for book in soup.select("article.product_pod"):
        title = book.h3.a["title"]
        price = book.select_one(".price_color").text
        availability = book.select_one(".availability").text.strip()

        products.append({
            "title": title,
            "price": price,
            "availability": availability
        })

    return products
