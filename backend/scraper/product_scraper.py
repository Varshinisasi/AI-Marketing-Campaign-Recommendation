import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_products(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []

    for item in soup.select(".product_pod"):
        title = item.h3.a["title"]
        price = item.select_one(".price_color").text
        availability = item.select_one(".availability").text.strip()

        products.append({
            "title": title,
            "price": price,
            "availability": availability
        })

    return products
