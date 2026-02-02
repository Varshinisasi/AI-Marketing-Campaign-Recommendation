import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AI Marketing Campaign System")

st.title("🧠 AI-Based Marketing Campaign Recommendation System")
st.subheader("Enter E-Commerce Store URL")

url = st.text_input("Enter product or category URL")

if st.button("Analyze Store"):
    if url.strip():
        with st.spinner("Scraping data..."):
            try:
                response = requests.get(
                    "http://localhost:8000/scrape",
                    params={"url": url},
                    timeout=30
                )
                data = response.json()

                st.success(f"Scraping Method Used: {data['scraping_method']}")
                df = pd.DataFrame(data["products"])
                st.dataframe(df)

            except Exception as e:
                st.error("Backend not running or invalid URL")
    else:
        st.warning("Please enter a valid URL")
