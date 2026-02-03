import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AI Marketing Campaign Scraper", layout="centered")

st.title("AI-Based Marketing Campaign Recommendation System")
st.subheader("Enter E-Commerce Store URL")

url = st.text_input("Website URL", "https://books.toscrape.com")

if st.button("Scrape Data"):
    with st.spinner("Scraping website..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/scrape",
                json={"url": url},
                timeout=15
            )

            data = response.json()

            if "results" in data and len(data["results"]) > 0:
                df = pd.DataFrame(data["results"])
                st.success("Scraping successful!")
                st.dataframe(df)
            else:
                st.error("No data found or website not supported")

        except Exception as e:
            st.error(f"Backend not running or invalid URL\n{e}")
