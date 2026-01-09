import streamlit as st
import pandas as pd

from src.clients.gamma import GammaClient
from src.core.filters import filter_candidates
from src.core.select_focus import select_focus_markets


st.set_page_config(page_title="Polymarket Dashboard", layout="wide")
st.title("Polymarket Market Dashboard")

max_hours = st.slider("Max hours to close (hours)", min_value=24, max_value=8760, value=48, step=24)
st.caption("Tip: If 0 candidates appear, increase the slider. Crypto markets often have 6+ months timeframe.")

if st.button("Refresh Data"):
    st.cache_data.clear()


@st.cache_data(ttl=300)
def load_markets(max_hours: int = 168):
    client = GammaClient()
    # Fetch only active, non-closed markets from API (much faster)
    all_markets = client.fetch_all_markets(active=True, closed=False)
    candidates = filter_candidates(all_markets, max_hours=max_hours)
    crypto, sports = select_focus_markets(candidates)
    return all_markets, candidates, crypto, sports


with st.spinner("Fetching markets from Polymarket..."):
    all_markets, candidates, crypto_market, sports_market = load_markets(max_hours=max_hours)

st.success(f"Loaded {len(all_markets)} active markets, {len(candidates)} candidates ({max_hours}h, orderbook enabled)")

# Focus Markets
st.header("Focus Markets (1 Crypto + 1 Sports)")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Crypto Market")
    if crypto_market:
        st.markdown(f"**{crypto_market.question}**")
        st.markdown(f"- **Category:** {crypto_market.category}")
        st.markdown(f"- **Closes in:** {crypto_market.hours_to_close:.2f} hours")
        st.markdown(f"- **YES Price:** {crypto_market.yes_price or 'N/A'}")
        st.markdown(f"- **NO Price:** {crypto_market.no_price or 'N/A'}")
        st.markdown(f"- **ID:** `{crypto_market.id}`")
        if crypto_market.slug:
            st.markdown(f"- **Slug:** `{crypto_market.slug}`")
    else:
        st.warning("No crypto market found matching criteria")

with col2:
    st.subheader("Sports Market")
    if sports_market:
        st.markdown(f"**{sports_market.question}**")
        st.markdown(f"- **Category:** {sports_market.category}")
        st.markdown(f"- **Closes in:** {sports_market.hours_to_close:.2f} hours")
        st.markdown(f"- **YES Price:** {sports_market.yes_price or 'N/A'}")
        st.markdown(f"- **NO Price:** {sports_market.no_price or 'N/A'}")
        st.markdown(f"- **ID:** `{sports_market.id}`")
        if sports_market.slug:
            st.markdown(f"- **Slug:** `{sports_market.slug}`")
    else:
        st.warning("No sports market found matching criteria")

st.divider()

# Candidate Markets Table
st.header("Candidate Markets")

if "filter_valid_prices" not in st.session_state:
    st.session_state.filter_valid_prices = False

col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    if st.button("Filter Valid Prices" if not st.session_state.filter_valid_prices else "Show All"):
        st.session_state.filter_valid_prices = not st.session_state.filter_valid_prices

if candidates:
    df = pd.DataFrame([m.to_dict() for m in candidates])

    if st.session_state.filter_valid_prices:
        df = df[df["yes_price"].notna() & df["no_price"].notna()]
        st.info(f"Showing {len(df)} markets with valid prices")

    display_cols = ["category", "question", "endDate", "hours_to_close", "yes_price", "no_price", "id", "slug", "price_note"]
    extra_cols = ["enableOrderBook", "yes_token_id", "no_token_id", "invalid_reason"]

    with st.expander("Show additional columns"):
        if st.checkbox("Include token IDs and order book status"):
            display_cols.extend(extra_cols)

    display_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, height=400)
else:
    st.warning("No candidate markets found matching all criteria")

st.divider()

# All Markets
with st.expander("View All Active Markets"):
    st.markdown(f"Total active markets: **{len(all_markets)}**")
    if all_markets:
        all_df = pd.DataFrame([m.to_dict() for m in all_markets[:500]])
        st.dataframe(all_df, use_container_width=True, height=300)
        if len(all_markets) > 500:
            st.caption(f"Showing first 500 of {len(all_markets)} markets")

st.divider()
st.caption("Data source: Polymarket Gamma API | Refresh page to update data")
