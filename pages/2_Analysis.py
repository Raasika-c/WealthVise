# pages/2_Analysis.py — WealthVise Multi-Agent Analysis
# M4 owns this file. Agents will be wired in Phase 3 (Day 6-8).

# Third-party
import streamlit as st

# Internal
from config import ALLOWED_SYMBOLS, DISCLAIMER

# ── Session guard ─────────────────────────────────────────────────────────────
if "username" not in st.session_state:
    st.warning("Please log in from the home page.")
    st.stop()

# ── Page layout ───────────────────────────────────────────────────────────────
st.title("🔍 Stock Analysis")
st.markdown("Select a symbol and your intended action. All 7 AI agents will evaluate the trade.")

col1, col2 = st.columns(2)
with col1:
    symbol = st.selectbox("📌 Stock Symbol", ALLOWED_SYMBOLS)
with col2:
    intent = st.selectbox("🎯 Your Intent", ["BUY", "SELL", "HOLD"])

run = st.button("▶ Run Analysis", use_container_width=True, type="primary")

if run:
    st.info(
        "🔧 **Agents are being built by team members (Days 3–8).**\n\n"
        "Once M1, M2, and M3 push their branches and M4 wires the orchestrator, "
        "this page will show live results."
    )

    # ── Placeholder spinners — shows the flow to the team ────────────────────
    steps = [
        ("📡 Market Analysis Agent",    "M1"),
        ("🗞️ Sentiment Agent",           "M2"),
        ("🤖 Prediction Agent",          "M3"),
        ("💼 Portfolio Agent",           "M3"),
        ("⚠️ Risk Agent",                "M1"),
        ("🧠 Strategy Validation Agent", "M3"),
        ("📝 Explainability Agent",      "M2"),
    ]
    for step_label, owner in steps:
        with st.spinner(f"{step_label} ({owner}) …"):
            import time
            time.sleep(0.3)
        st.success(f"{step_label} — ✅ ready (stub)")

    st.divider()
    st.markdown("### 🏁 Verdict")
    st.warning("⏳ Awaiting agent integration (Phase 3)")

st.divider()
st.warning(DISCLAIMER)
