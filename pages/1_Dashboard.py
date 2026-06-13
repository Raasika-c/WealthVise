# pages/1_Dashboard.py — WealthVise Portfolio Dashboard
# M4 owns this file.

# Standard library
from datetime import datetime

# Third-party
import plotly.express as px
import streamlit as st

# Internal
from config import ALLOWED_SYMBOLS, DISCLAIMER
from utils.db import load_portfolio, save_portfolio

# ── Session guard ─────────────────────────────────────────────────────────────
if "username" not in st.session_state:
    st.warning("Please log in from the home page.")
    st.stop()

username: str = st.session_state["username"]
name: str     = st.session_state.get("name", username)

# ── Page layout ───────────────────────────────────────────────────────────────
st.title("📊 Portfolio Dashboard")
st.caption(f"Logged in as **{name}**  •  {datetime.now().strftime('%d %b %Y, %H:%M')}")

# ── Load saved portfolio ──────────────────────────────────────────────────────
saved_portfolio: dict = load_portfolio(username)

# ── Portfolio edit form ───────────────────────────────────────────────────────
st.subheader("✏️ Edit Portfolio Allocation")
st.markdown("Enter the **percentage weight** (0–100) for each symbol. Weights must sum to ~100.")

with st.form("portfolio_form"):
    cols = st.columns(5)
    portfolio_input: dict[str, float] = {}

    for i, symbol in enumerate(ALLOWED_SYMBOLS):
        default_val = float(saved_portfolio.get(symbol, 0.0))
        val = cols[i % 5].number_input(
            label=symbol,
            min_value=0.0,
            max_value=100.0,
            value=default_val,
            step=1.0,
            key=f"portfolio_{symbol}",
        )
        portfolio_input[symbol] = val

    submitted = st.form_submit_button("💾 Save Portfolio", use_container_width=True)

if submitted:
    # Filter out zero-weight symbols
    filtered = {k: v for k, v in portfolio_input.items() if v > 0}
    total = sum(filtered.values())

    if not filtered:
        st.error("❌ Portfolio cannot be empty. Enter at least one allocation.")
    elif not (90.0 <= total <= 110.0):
        st.error(f"❌ Weights sum to **{total:.1f}%** — must be between 90% and 110%.")
    else:
        save_portfolio(username, filtered)
        st.success(f"✅ Portfolio saved! Total weight: **{total:.1f}%**")
        saved_portfolio = filtered

# ── Display metrics ───────────────────────────────────────────────────────────
active_holdings = {k: v for k, v in saved_portfolio.items() if v > 0}

if active_holdings:
    st.divider()
    st.subheader("📈 Portfolio Overview")

    total_weight      = sum(active_holdings.values())
    largest_symbol    = max(active_holdings, key=active_holdings.get)
    largest_pct       = active_holdings[largest_symbol]
    diversification   = round(100 - largest_pct, 1)
    concentration     = round(largest_pct, 1)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Holdings",           len(active_holdings))
    m2.metric("Largest Position",   f"{largest_symbol} ({largest_pct:.1f}%)")
    m3.metric("Diversification",    f"{diversification}%")
    m4.metric("Concentration Risk", f"{concentration}%")

    # ── Allocation pie chart ──────────────────────────────────────────────────
    st.subheader("🥧 Allocation Breakdown")
    fig_pie = px.pie(
        names=list(active_holdings.keys()),
        values=list(active_holdings.values()),
        title="Portfolio Allocation",
        hole=0.35,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(showlegend=True, margin=dict(t=40, b=0))
    st.plotly_chart(fig_pie, use_container_width=True)

    # ── Price history charts ──────────────────────────────────────────────────
    st.subheader("📉 Price History (1 Year)")
    selected_symbol = st.selectbox(
        "Select symbol to view chart",
        options=list(active_holdings.keys()),
    )

    if selected_symbol:
        try:
            import yfinance as yf

            @st.cache_data(ttl=300)
            def _get_history(sym: str):
                ticker = yf.Ticker(sym)
                return ticker.history(period="1y")

            hist = _get_history(selected_symbol)

            if hist.empty:
                st.warning(f"No price data found for {selected_symbol}.")
            else:
                fig_line = px.line(
                    hist,
                    x=hist.index,
                    y="Close",
                    title=f"{selected_symbol} — 1-Year Closing Price",
                    labels={"Close": "Price (USD)", "Date": ""},
                )
                fig_line.update_layout(margin=dict(t=40, b=0))
                st.plotly_chart(fig_line, use_container_width=True)

        except Exception as exc:
            st.error(f"Could not load price data: {exc}")

else:
    st.info("ℹ️ No portfolio saved yet. Use the form above to add your holdings.")

st.divider()
st.caption(DISCLAIMER)
