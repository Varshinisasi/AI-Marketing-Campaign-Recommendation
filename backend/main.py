from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.scraper.generic_scraper import generic_scrape

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
        return {"results": products}
    except Exception as e:
        return {"error": str(e)}
