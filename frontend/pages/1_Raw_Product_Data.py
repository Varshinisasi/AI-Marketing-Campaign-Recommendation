import streamlit as st
import pandas as pd

st.set_page_config(page_title="Raw Product Data", layout="wide")

st.title("Raw Product Data")

results = st.session_state.get("scraped_results")

if not results:
    st.info("Go to the Home page, enter a store URL, and click 'Scrape Data' first.")
else:
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

