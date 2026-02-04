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
                st.success("Scraping successful!")
                st.dataframe(df)
            else:
                st.error("No data found or website not supported")

        except Exception as e:
            st.error(f"Backend not running or invalid URL\n{e}")
