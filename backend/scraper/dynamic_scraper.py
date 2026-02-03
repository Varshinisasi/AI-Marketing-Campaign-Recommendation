from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def scrape_dynamic(url):
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        titles = soup.find_all(["h1", "h2", "h3"])
        products = [{"product_name": t.get_text(strip=True)} for t in titles]

        return {"products": products}

    except Exception:
        return None
