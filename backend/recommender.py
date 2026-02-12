from typing import List, Dict, Any
import statistics


def _to_float(value, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def _to_int(value, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def analyze_products(products: List[Dict[str, Any]], source_url: str) -> Dict[str, Any]:
    """
    Lightweight heuristic-based analysis over scraped products.

    Returns:
        {
          "summary": {...},
          "top_products": [...],
          "platform_recommendations": [...],
          "discount_suggestions": [...],
          "ad_captions": [...]
        }
    """
    if not products:
        return {
            "summary": {"message": "No products found for analysis."},
            "top_products": [],
            "platform_recommendations": [],
            "discount_suggestions": [],
            "ad_captions": [],
        }

    # Compute simple numeric features
    enriched = []
    for p in products:
        rating = _to_float(p.get("rating"), 0.0)  # expected 0–5
        reviews = _to_int(p.get("reviews"), 0)

        # crude price parsing: strip currency and commas
        raw_price = str(p.get("price", "")).replace(",", "")
        price_num = 0.0
        for ch in raw_price:
            if ch.isdigit() or ch in ".-":
                continue
        try:
            # pull first number substring if present
            import re

            m = re.search(r"\d+(\.\d+)?", raw_price)
            if m:
                price_num = float(m.group(0))
        except Exception:
            price_num = 0.0

        # engagement / priority score
        score = rating * (1 + reviews / 10.0)

        enriched.append(
            {
                **p,
                "_rating_num": rating,
                "_reviews_num": reviews,
                "_price_num": price_num,
                "_score": score,
            }
        )

    # Sort by score (best products to promote)
    top_products = sorted(enriched, key=lambda x: x["_score"], reverse=True)[:5]

    # Summary stats
    ratings = [p["_rating_num"] for p in enriched if p["_rating_num"] > 0]
    prices = [p["_price_num"] for p in enriched if p["_price_num"] > 0]

    avg_rating = round(statistics.mean(ratings), 2) if ratings else 0.0
    avg_price = round(statistics.mean(prices), 2) if prices else 0.0

    summary = {
        "source_url": source_url,
        "product_count": len(products),
        "avg_rating": avg_rating,
        "avg_price": avg_price,
    }

    # Platform recommendations (very simple rules)
    platforms = []
    if avg_price >= 80 or any(p["_price_num"] >= 100 for p in enriched):
        platforms.append(
            "Instagram & Google Ads: Visual, higher-ticket products perform well here."
        )
    if avg_price < 80:
        platforms.append(
            "Facebook & WhatsApp: Good for mid- to low-priced, impulse-friendly items."
        )
    if avg_rating >= 4.2:
        platforms.append(
            "Email campaigns: Leverage strong reviews to upsell and cross-sell bestsellers."
        )
    if not platforms:
        platforms.append(
            "Start with Instagram + Email, then refine channels based on campaign results."
        )

    # Discount suggestions for top products
    discount_suggestions = []
    for p in top_products:
        rating = p["_rating_num"]
        reviews = p["_reviews_num"]
        title = p.get("title") or "This product"

        if rating >= 4.5 and reviews >= 20:
            suggestion = (
                f"{title}: bestseller — run a 5–10% limited-time discount and highlight reviews."
            )
        elif rating >= 4.0 and reviews >= 5:
            suggestion = (
                f"{title}: good traction — try a 10–15% discount or bundle with related items."
            )
        else:
            suggestion = (
                f"{title}: low social proof — focus on organic content first, then test small-budget ads."
            )

        discount_suggestions.append(suggestion)

    # Simple AI-like ad captions for top products
    ad_captions = []
    for p in top_products[:3]:
        title = p.get("title") or "this product"
        price = p.get("price") or ""
        rating = p.get("rating") or ""

        base_caption = (
            f"Fall in love with {title} — a timeless piece designed for everyday wear. "
        )
        if rating and rating != "N/A":
            base_caption += f"Rated {rating}/5 by shoppers. "
        if price:
            base_caption += f"Now available at {price}. "
        base_caption += "Tap to shop and elevate your wardrobe. #NewArrivals #ShopNow"

        ad_captions.append(
            {
                "product": title,
                "platform": "Instagram",
                "caption": base_caption,
            }
        )

    return {
        "summary": summary,
        "top_products": [
            {
                "title": p.get("title"),
                "price": p.get("price"),
                "rating": p.get("rating"),
                "reviews": p.get("reviews"),
                "availability": p.get("availability"),
            }
            for p in top_products
        ],
        "platform_recommendations": platforms,
        "discount_suggestions": discount_suggestions,
        "ad_captions": ad_captions,
    }

