import streamlit as st

st.set_page_config(page_title="Suggested Marketing Platforms", layout="centered")

st.title("Suggested Marketing Platforms")

insights = st.session_state.get("scraped_insights") or {}
platforms = insights.get("platform_recommendations") or []

if not platforms:
    st.info("Go to the Home page, enter a store URL, and click 'Scrape Data' first.")
else:
    for p in platforms:
        st.markdown(f"- {p}")

