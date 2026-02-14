import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AI Marketing Campaign Scraper", layout="centered")

st.title("AI-Based Marketing Campaign Recommendation System")
st.subheader("Enter E-Commerce Store URL")

# Keep scraped data in session so the user can navigate to other pages
if "scraped_results" not in st.session_state:
    st.session_state["scraped_results"] = None
if "scraped_insights" not in st.session_state:
    st.session_state["scraped_insights"] = None

url = st.text_input("Website URL", "Enter your website URL")

if st.button("Scrape Data"):
    with st.spinner("Scraping website..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/scrape",
                json={"url": url},
                timeout=60,
            )

            data = response.json()

            # Show detailed feedback based on backend response
            if "error" in data:
                st.error(f"Backend error: {data['error']}")
                st.session_state["scraped_results"] = None
                st.session_state["scraped_insights"] = None
            elif "results" in data and len(data["results"]) > 0:
                st.session_state["scraped_results"] = data["results"]
                st.session_state["scraped_insights"] = data.get("insights", {})
                st.success(
                    "Scraping and analysis successful."
                )
            else:
                st.session_state["scraped_results"] = None
                st.session_state["scraped_insights"] = None
                st.error("No data found or website not supported")

        except Exception as e:
            st.session_state["scraped_results"] = None
            st.session_state["scraped_insights"] = None
            st.error(f"Backend not running or invalid URL\n{e}")

