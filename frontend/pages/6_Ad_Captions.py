import streamlit as st

st.set_page_config(page_title="AI-Generated Ad Captions", layout="centered")

st.title("AI-Generated Ad Captions")

insights = st.session_state.get("scraped_insights") or {}
captions = insights.get("ad_captions") or []

if not captions:
    st.info("Go to the Home page, enter a store URL, and click 'Scrape Data' first.")
else:
    for c in captions:
        st.markdown(f"**{c.get('product')} ({c.get('platform')})**")
        st.write(c.get("caption"))
        st.markdown("---")

