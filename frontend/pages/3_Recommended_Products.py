import streamlit as st
import pandas as pd

st.set_page_config(page_title="Recommended Products", layout="wide")

st.title("Recommended Products to Promote")

insights = st.session_state.get("scraped_insights") or {}
top_products = insights.get("top_products") or []

if not top_products:
    st.info("Go to the Home page, enter a store URL, and click 'Scrape Data' first.")
else:
    st.dataframe(pd.DataFrame(top_products), use_container_width=True)

