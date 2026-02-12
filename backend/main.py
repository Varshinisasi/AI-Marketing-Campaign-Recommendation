from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.scraper.generic_scraper import generic_scrape
from backend.recommender import analyze_products
from backend.database.mongo_db import save_products

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"status": "running"}


@app.post("/scrape")
def scrape_site(data: dict):
    url = data.get("url")
    if not url:
        return {"error": "URL not provided"}

    try:
        products = generic_scrape(url)

        # Persist raw product data for later analysis / reuse
        try:
            # attach source URL to each product document
            to_save = [{**p, "source_url": url} for p in products]
            save_products(to_save)
        except Exception:
            # MongoDB is optional – ignore persistence errors
            pass

        # Run heuristic AI-style marketing analysis
        insights = analyze_products(products, url)

        return {
            "results": products,
            "insights": insights,
        }
    except Exception as e:
        return {"error": str(e)}
