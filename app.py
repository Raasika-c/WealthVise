# app.py — WealthVise Main Entry Point
# M4 owns this file.

# Standard library
import os

# Third-party
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Internal
from config import APP_NAME, APP_TAGLINE, DISCLAIMER
from utils.db import init_db

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Database init ─────────────────────────────────────────────────────────────
init_db()

# ── Load auth config ──────────────────────────────────────────────────────────
CONFIG_PATH = "config.yaml"

def _load_auth_config() -> dict:
    """Load auth config from config.yaml; create a default one if missing."""
    if not os.path.exists(CONFIG_PATH):
        # Default demo config — team replaces before deploy
        default = {
            "credentials": {
                "usernames": {
                    "demo": {
                        "name": "Demo User",
                        # bcrypt hash of "demo123"
                        "password": "$2b$12$KIX9UvRLmUfMwJ6qBh9Q4.sVlAi97BbqePkVHgxdAPV8bDkRb7Hjm",
                    }
                }
            },
            "cookie": {
                "expiry_days": 1,
                "key": "wealthvise_secret_key",
                "name": "wealthvise_cookie",
            },
            "preauthorized": {"emails": []},
        }
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(default, f)
        return default

    with open(CONFIG_PATH) as f:
        return yaml.load(f, Loader=SafeLoader)


config = _load_auth_config()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# ── Login wall ────────────────────────────────────────────────────────────────
name, authentication_status, username = authenticator.login("Login to WealthVise", "main")

if authentication_status is False:
    st.error("❌ Incorrect username or password.")
    st.stop()

if authentication_status is None:
    # Show landing hero while not logged in
    st.markdown(
        f"""
        <div style="text-align:center; padding: 4rem 0 2rem;">
            <h1 style="font-size:3rem;">📈 {APP_NAME}</h1>
            <p style="font-size:1.2rem; color:#888;">{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("👆 Enter your credentials above to get started.")
    st.stop()

# ── Authenticated — store session state ──────────────────────────────────────
st.session_state["username"] = username
st.session_state["name"]     = name

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## 📈 {APP_NAME}")
    st.markdown(f"*{APP_TAGLINE}*")
    st.divider()
    st.markdown(f"👋 Welcome, **{name}**!")
    st.divider()
    st.markdown("### Navigation")
    st.page_link("pages/1_Dashboard.py",  label="📊 Dashboard",  icon="📊")
    st.page_link("pages/2_Analysis.py",   label="🔍 Analysis",   icon="🔍")
    st.page_link("pages/3_Chatbot.py",    label="💬 Chatbot",    icon="💬")
    st.divider()
    authenticator.logout("Logout", "sidebar")
    st.divider()
    st.caption(DISCLAIMER)

# ── Home page content ─────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="text-align:center; padding: 3rem 0 1rem;">
        <h1 style="font-size:2.8rem;">📈 {APP_NAME}</h1>
        <p style="font-size:1.15rem; color:#888;">{APP_TAGLINE}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    st.info("### 📊 Dashboard\nView your portfolio allocation and live price charts.")
with col2:
    st.info("### 🔍 Analysis\nRun all 7 AI agents and get a BUY / SELL / HOLD verdict.")
with col3:
    st.info("### 💬 Chatbot\nAsk investing questions powered by Groq LLaMA 3.")

st.divider()
st.warning(DISCLAIMER)

