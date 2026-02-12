import streamlit as st

st.set_page_config(page_title="Discount & Campaign Suggestions", layout="centered")

st.title("Discount & Campaign Suggestions")

insights = st.session_state.get("scraped_insights") or {}
discounts = insights.get("discount_suggestions") or []

if not discounts:
    st.info("Go to the Home page, enter a store URL, and click 'Scrape Data' first.")
else:
    for d in discounts:
        st.markdown(f"- {d}")

