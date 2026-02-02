import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AI Marketing Campaign System")

st.title("🧠 AI-Based Marketing Campaign Recommendation System")
st.subheader("Enter E-Commerce Store URL")

url = st.text_input("Enter product or category URL")

if st.button("Analyze Store"):
    if url:
        with st.spinner("Scraping data..."):
            response = requests.get(
                "http://localhost:8000/scrape",
                params={"url": url}
            )
            data = response.json()

        st.success(f"Scraping Method Used: {data['scraping_method']}")
        df = pd.DataFrame(data["products"])
        st.table(df)
    else:
        st.warning("Please enter a valid URL")
