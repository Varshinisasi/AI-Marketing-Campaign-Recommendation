import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_static(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []

    for item in soup.select(".product, .thumbnail, .item"):
        name = item.find("h2") or item.find("h3")
        price = item.find(class_="price")

        products.append({
            "name": name.text.strip() if name else "N/A",
            "price": price.text.strip() if price else "N/A"
        })

    return products
