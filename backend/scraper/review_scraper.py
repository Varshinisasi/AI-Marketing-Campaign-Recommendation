import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_reviews(product_url):
    reviews = []

    response = requests.get(product_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    review_blocks = soup.find_all("div", class_="review")

    for block in review_blocks:
        try:
            review_text = block.find("p").text.strip()
            reviews.append(review_text)
        except:
            continue

    return reviews
