from fastapi import FastAPI
from backend.scraper.static_scraper import scrape_static
from backend.scraper.dynamic_scraper import scrape_dynamic
from backend.scraper.utils import is_dynamic_site


app = FastAPI(title="AI Marketing Campaign Scraper")

@app.get("/scrape")
def scrape(url: str):
    if is_dynamic_site(url):
        data = scrape_dynamic(url)
        method = "Dynamic (Selenium)"
    else:
        data = scrape_static(url)
        method = "Static (BeautifulSoup)"

    return {
        "scraping_method": method,
        "products": data
    }
