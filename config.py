# config.py  —  Owned by M4. This stub lets M1 develop locally.
# DO NOT commit your real keys. Replace with your own .env values.
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    def get_secret(key: str) -> str:
        try:
            return st.secrets[key]
        except Exception:
            return os.getenv(key, "")
except ImportError:
    def get_secret(key: str) -> str:
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

DISCLAIMER = (
    "⚠️ WealthVise is for educational purposes only. "
    "This is not financial advice. "
    "Consult a SEBI-registered advisor before investing."
)
