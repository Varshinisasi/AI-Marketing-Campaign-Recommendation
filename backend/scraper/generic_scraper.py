import json
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

# Selenium imports for JS-rendered pages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def _get_text_or_none(element) -> Optional[str]:
    """Safely get stripped text from a BeautifulSoup element."""
    if not element:
        return None
    text = element.get_text(strip=True)
    return text or None


def _is_shopify(html: str, soup: BeautifulSoup) -> bool:
    """Heuristic check whether a site is built on Shopify."""
    if "cdn.shopify.com" in html:
        return True

    # Common Shopify markers
    if soup.find("meta", {"name": "shopify-digital-wallet"}):
        return True

    scripts_text = " ".join(
        s.get_text(" ", strip=True)[:200].lower()
        for s in soup.find_all("script")
    )
    if "shopify" in scripts_text:
        return True

    return False


def _extract_products_from_ld(ld_obj) -> List[Dict]:
    """Extract product info (title/price/availability/rating/reviews) from JSON-LD objects."""
    products: List[Dict] = []

    def handle(obj):
        if isinstance(obj, list):
            for item in obj:
                handle(item)
            return

        if not isinstance(obj, dict):
            return

        type_field = obj.get("@type")
        if isinstance(type_field, list):
            types = [t.lower() for t in type_field if isinstance(t, str)]
        elif isinstance(type_field, str):
            types = [type_field.lower()]
        else:
            types = []

        if "product" in types:
            name = obj.get("name") or obj.get("headline")

            offers = obj.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}

            price = (
                offers.get("price")
                or offers.get("priceSpecification", {}).get("price")
            )
            availability = None
            if "availability" in offers:
                availability = str(offers.get("availability")).split("/")[-1]

            # Rating and reviews from aggregateRating / review fields
            rating = None
            reviews = None

            aggregate = obj.get("aggregateRating") or {}
            if isinstance(aggregate, list):
                aggregate = aggregate[0] if aggregate else {}

            if isinstance(aggregate, dict):
                raw_rating = aggregate.get("ratingValue")
                best_rating = aggregate.get("bestRating")

                # Normalize rating to a 0–5 scale where possible
                try:
                    if raw_rating is not None:
                        rv = float(raw_rating)
                        if best_rating is not None:
                            br = float(best_rating)
                            if br > 0:
                                rating = round((rv / br) * 5, 2)
                            else:
                                rating = round(rv, 2)
                        else:
                            # Assume already out of 5
                            rating = round(rv, 2)
                except (TypeError, ValueError):
                    rating = None

                reviews = (
                    aggregate.get("reviewCount")
                    or aggregate.get("ratingCount")
                    or reviews
                )

            # If explicit reviews list is present, use its length as count
            if reviews is None and isinstance(obj.get("review"), list):
                reviews = len(obj["review"])

            # Clean up reviews into an integer if possible
            if isinstance(reviews, str):
                m = re.search(r"\d+", reviews)
                if m:
                    try:
                        reviews = int(m.group(0))
                    except ValueError:
                        reviews = None

            if name or price:
                # Fill missing fields with readable placeholders
                products.append(
                    {
                        "title": (name or "Unknown title"),
                        "price": str(price) if price is not None else "N/A",
                        "availability": availability or "Unknown",
                        "rating": (
                            f"{rating:.1f}" if isinstance(rating, (int, float)) else "N/A"
                        ),
                        "reviews": (
                            str(int(reviews))
                            if isinstance(reviews, (int, float))
                            else "N/A"
                        ),
                    }
                )

        # ItemList with embedded products
        if any(t in ("itemlist",) for t in types) and "itemListElement" in obj:
            for el in obj["itemListElement"]:
                # schema.org ItemListElement can wrap item
                item = el.get("item") if isinstance(el, dict) else el
                handle(item)

    handle(ld_obj)
    return products


def _render_with_selenium(url: str, timeout: int = 15) -> str:
    """
    Use headless Chrome (Selenium) to render JavaScript-heavy pages and
    return the final page source.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    try:
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        # simple wait; for complex sites you'd add explicit waits
        driver.implicitly_wait(5)
        html = driver.page_source
    finally:
        driver.quit()

    return html


def _parse_products_from_soup(soup: BeautifulSoup) -> List[Dict]:
    """
    Try to scrape product-like information from *any* e-commerce page.

    Strategy:
    1. Fetch the page HTML.
    2. Try several common product container selectors (works for many themes).
    3. Inside each container, try common patterns for title / price / availability.
    4. If nothing product-like is found, fall back to the original books.toscrape.com logic.
    """

    products: List[Dict] = []

    # 1. Try a set of generic "product card" selectors that work on many sites
    container_selectors = [
        "[data-product-id]",
        "[data-product-id]",
        "[itemtype*='Product']",
        ".product-card",
        ".product-grid-item",
        ".product-item",
        ".product",
        ".product_pod",  # books.toscrape.com
        "li.product",
        "article.product",
    ]

    product_cards = []
    for sel in container_selectors:
        product_cards = soup.select(sel)
        if product_cards:
            break

    # 2. If we found product-like containers, parse each one
    if product_cards:
        for card in product_cards:
            # Title candidates
            title = (
                card.get("data-name")
                or card.get("data-product-name")
                or _get_text_or_none(card.select_one("[itemprop='name']"))
                or _get_text_or_none(card.select_one(".product-title"))
                or _get_text_or_none(card.select_one(".product-name"))
                or _get_text_or_none(card.select_one("h3"))
                or _get_text_or_none(card.select_one("h2"))
            )

            # Price candidates
            price_el = (
                card.select_one("[itemprop='price']")
                or card.select_one(".price")
                or card.select_one(".product-price")
                or card.select_one("[class*='price']")
            )
            price = None
            if price_el:
                price = price_el.get("content") or _get_text_or_none(price_el)

            # Availability candidates
            availability_el = (
                card.select_one("[itemprop='availability']")
                or card.select_one(".availability")
                or card.select_one("[class*='stock']")
            )
            availability = None
            if availability_el:
                availability = (
                    availability_el.get("content")
                    or _get_text_or_none(availability_el)
                )

            # Rating candidates
            rating_el = (
                card.select_one("[itemprop='ratingValue']")
                or card.select_one("[class*='rating']")
                or card.select_one("[class*='star']")
            )
            rating = None
            if rating_el:
                text = rating_el.get_text(" ", strip=True)
                # Prefer patterns that explicitly mention "out of 5" or "/5"
                m = re.search(
                    r"(\d+(\.\d+)?)\s*(?:/|out of)\s*5", text, flags=re.IGNORECASE
                )
                if m:
                    rating = m.group(1)
                else:
                    # Fallback: any first number like "4.5" or "4"
                    m = re.search(r"\d+(\.\d+)?", text)
                    if m:
                        rating = m.group(0)

            # Reviews count candidates
            reviews_el = (
                card.select_one("[itemprop='reviewCount']")
                or card.select_one("[class*='review']")
                or card.select_one("[class*='reviews']")
            )
            reviews = None
            if reviews_el:
                m = re.search(r"\d+", reviews_el.get_text(" ", strip=True))
                if m:
                    reviews = m.group(0)

            # Build a product row if we have at least a title or price.
            # Try extra fallbacks so cells are not blank.
            if title or price:
                # Extra title fallbacks: aria-label, anchor title, image alt
                if not title:
                    title = (
                        card.get("aria-label")
                        or _get_text_or_none(card.select_one("a[title]"))
                        or card.select_one("img").get("alt")
                        if card.select_one("img")
                        else None
                    )

                products.append(
                    {
                        "title": title or "Unknown title",
                        "price": price or "N/A",
                        "availability": availability or "Unknown",
                        "rating": rating or "N/A",
                        "reviews": reviews or "N/A",
                    }
                )

    # 3. Fallback: explicit books.toscrape.com logic if nothing found
    if not products:
        for book in soup.select("article.product_pod"):
            title = book.h3.a.get("title") if book.h3 and book.h3.a else None
            price_el = book.select_one(".price_color")
            availability_el = book.select_one(".availability")

            # Rating on books.toscrape.com is via classes like "star-rating Three"
            rating_el = book.select_one("p.star-rating")
            rating = None
            if rating_el and rating_el.has_attr("class"):
                rating_classes = [
                    cls for cls in rating_el["class"] if cls.lower() != "star-rating"
                ]
                if rating_classes:
                    word = rating_classes[0].lower()
                    mapping = {
                        "one": 1,
                        "two": 2,
                        "three": 3,
                        "four": 4,
                        "five": 5,
                    }
                    if word in mapping:
                        rating = mapping[word]

            products.append(
                {
                    "title": title or _get_text_or_none(book.h3) or "Unknown title",
                    "price": _get_text_or_none(price_el) or "N/A",
                    "availability": _get_text_or_none(availability_el) or "Unknown",
                    "rating": f"{rating:.1f}" if isinstance(rating, (int, float)) else "N/A",
                    "reviews": "N/A",
                }
            )

    return products


def generic_scrape(url: str) -> List[Dict]:
    """
    High-level entry point:
    1. Try static HTML with requests.
    2. If we don't find any products, try JS-rendered HTML via Selenium.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    # 1. Try simple static HTML fetch
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    # 1a. If this looks like a Shopify site, prefer JSON-LD Product data
    products: List[Dict] = []
    if _is_shopify(html, soup):
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                ld = json.loads(script.string or script.text or "{}")
            except Exception:
                continue
            products.extend(_extract_products_from_ld(ld))

        if products:
            return products

    # 1b. Generic HTML-based parsing
    products = _parse_products_from_soup(soup)
    if products:
        return products

    # 2. Fallback to Selenium for JS-rendered content
    try:
        rendered_html = _render_with_selenium(url)
        rendered_soup = BeautifulSoup(rendered_html, "html.parser")

        # 2a. Shopify JSON-LD on rendered page
        if _is_shopify(rendered_html, rendered_soup):
            for script in rendered_soup.find_all(
                "script", type="application/ld+json"
            ):
                try:
                    ld = json.loads(script.string or script.text or "{}")
                except Exception:
                    continue
                products.extend(_extract_products_from_ld(ld))

            if products:
                return products

        # 2b. Generic HTML-based parsing on rendered content
        products = _parse_products_from_soup(rendered_soup)
        return products
    except Exception:
        # If Selenium fails (e.g., no browser on machine), just return whatever we found
        return products
