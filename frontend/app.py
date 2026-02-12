import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AI Marketing Campaign Scraper", layout="centered")

st.title("AI-Based Marketing Campaign Recommendation System")
st.subheader("Enter E-Commerce Store URL")

url = st.text_input("Website URL", "https://deyga.in")

if st.button("Scrape Data"):
    with st.spinner("Scraping website..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/scrape",
                json={"url": url},
                # Increase timeout because some sites (and first-time Selenium runs)
                # can take longer than 15 seconds to respond.
                timeout=60
            )

            data = response.json()

            # Show detailed feedback based on backend response
            if "error" in data:
                st.error(f"Backend error: {data['error']}")
            elif "results" in data and len(data["results"]) > 0:
                df = pd.DataFrame(data["results"])

                st.success("Scraping & analysis successful!")

                st.markdown("### Raw Product Data")
                st.dataframe(df)

                insights = data.get("insights", {})

                # Summary section
                summary = insights.get("summary", {})
                if summary:
                    st.markdown("### Store Summary")
                    st.write(
                        {
                            "Products scraped": summary.get("product_count"),
                            "Average rating": summary.get("avg_rating"),
                            "Average price (approx.)": summary.get("avg_price"),
                        }
                    )

                # Top products to promote
                top_products = insights.get("top_products") or []
                if top_products:
                    st.markdown("### Recommended Products to Promote")
                    st.dataframe(pd.DataFrame(top_products))

                # Platform recommendations
                platforms = insights.get("platform_recommendations") or []
                if platforms:
                    st.markdown("### Suggested Marketing Platforms")
                    for p in platforms:
                        st.markdown(f"- {p}")

                # Discount ideas
                discounts = insights.get("discount_suggestions") or []
                if discounts:
                    st.markdown("### Discount & Campaign Suggestions")
                    for d in discounts:
                        st.markdown(f"- {d}")

                # AI-style ad captions
                captions = insights.get("ad_captions") or []
                if captions:
                    st.markdown("### AI-Generated Ad Captions")
                    for c in captions:
                        st.markdown(f"**{c.get('product')} ({c.get('platform')})**")
                        st.write(c.get("caption"))
                        st.markdown("---")
            else:
                st.error("No data found or website not supported")

        except Exception as e:
            st.error(f"Backend not running or invalid URL\n{e}")
