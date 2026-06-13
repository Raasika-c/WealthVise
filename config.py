# config.py  —  Owned by M4. This stub lets M1 develop locally.
# DO NOT commit your real keys. Replace with your own .env values.
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key: str) -> str:
    """Load secret from st.secrets (Streamlit Cloud) or .env (local)."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, "")

FINNHUB_KEY    = get_secret("FINNHUB_KEY")
NEWSAPI_KEY    = get_secret("NEWSAPI_KEY")
GROQ_API_KEY   = get_secret("GROQ_API_KEY")
REDDIT_ID      = get_secret("REDDIT_CLIENT_ID")
REDDIT_SECRET  = get_secret("REDDIT_SECRET")
REDDIT_AGENT   = "wealthvise_bot"

ALLOWED_SYMBOLS = [
    "AAPL", "TSLA", "NVDA", "MSFT", "GOOGL",
    "AMZN", "META", "AMD", "INTC", "NFLX"
]
DB_PATH = "portfolios.db"

DISCLAIMER = (
    "⚠️ WealthVise is for educational purposes only. "
    "This is not financial advice. "
    "Consult a SEBI-registered advisor before investing."
)
APP_NAME    = "WealthVise"
APP_TAGLINE = "Multi-Agent Intelligence for Smarter Investing"
