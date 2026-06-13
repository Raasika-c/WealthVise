
import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()
# ── NewsAPI setup ──────────────────────────────────────────────
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY") or st.secrets.get("NEWSAPI_KEY")
NEWSAPI_URL = "https://newsapi.org/v2/everything"
def register_newsapi():
    """Return a simple NewsAPI session with auth header."""
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {NEWSAPI_KEY}"})
    return session
# ── News fetcher ───────────────────────────────────────────────
def fetch_news(symbol: str, days: int = 3) -> list:
    """
    Pull headlines + descriptions for a ticker symbol via NewsAPI.
    Returns a list of dicts with keys: title, description, url, publishedAt
    """
    try:
        session = register_newsapi()
        from_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        params = {
            "q": symbol,
            "from": from_date,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 20,
        }
        resp = session.get(NEWSAPI_URL, params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        results = []
        for a in articles:
            results.append({
                "source": "newsapi",
                "symbol": symbol,
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "url": a.get("url", ""),
                "publishedAt": a.get("publishedAt", ""),
            })
        return results
    except Exception as e:
        print(f"NewsAPI fetch failed: {e}")
        return []
# ── Reddit skipped ─────────────────────────────────────────────
def fetch_reddit_posts(symbol: str, limit: int = 20) -> list:
    """
    Reddit skipped — returns empty list.
    Can be enabled later when Reddit API is available.
    """
    print("Reddit skipped — no API key available")
    return []
# ── Shared data schema (dict) ──────────────────────────────────
def get_news_data(symbol: str) -> dict:
    """
    Master function called by other agents.
    Returns a shared schema dict compatible with Member 3 / Member 4.
    """
    news   = fetch_news(symbol)
    reddit = fetch_reddit_posts(symbol)
    return {
        "symbol": symbol,
        "news_articles": news,
        "reddit_posts": reddit,
        "news_count": len(news),
        "reddit_count": len(reddit),
        "fetched_at": datetime.utcnow().isoformat(),
    }
# ── Quick Streamlit debug view ─────────────────────────────────
if __name__ == "__main__":
    st.title("Member 2 – News Debug")
    sym = st.text_input("Ticker", value="AAPL")
    if st.button("Fetch"):
        with st.spinner("Fetching..."):
            data = get_news_data(sym)
        st.json(data)
