import streamlit as st

st.set_page_config(page_title="Store Summary", layout="centered")

st.title("Store Summary")

insights = st.session_state.get("scraped_insights") or {}
summary = insights.get("summary")

if not summary:
    st.info("Go to the Home page, enter a store URL, and click 'Scrape Data' first.")
else:
    st.write(
        {
            "Source URL": summary.get("source_url"),
            "Products scraped": summary.get("product_count"),
            "Average rating": summary.get("avg_rating"),
            "Average price (approx.)": summary.get("avg_price"),
        }
    )

