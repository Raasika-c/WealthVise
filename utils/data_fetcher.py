# utils/data_fetcher.py  —  Member 1 (M1)
# Fetches market data from Finnhub (primary) and yfinance (fallback)

# 1. Standard library
import time
from datetime import datetime, timedelta

# 2. Third-party
import pandas as pd
import numpy as np
import requests
import yfinance as yf
import finnhub
import streamlit as st

# 3. Internal
from config import FINNHUB_KEY, ALLOWED_SYMBOLS

# ---------------------------------------------------------------------------
# Finnhub client (module-level, created once)
# ---------------------------------------------------------------------------
_finnhub_client = finnhub.Client(api_key=FINNHUB_KEY)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _rate_limit() -> None:
    """Pause 0.5 s between sequential Finnhub calls to respect the free tier."""
    time.sleep(0.5)


# ---------------------------------------------------------------------------
# Quote
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def get_quote(symbol: str) -> dict:
    """
    Fetch the latest quote for *symbol* from Finnhub.
    Falls back to yfinance if Finnhub fails.

    Returns:
        {
            "symbol": str,
            "current_price": float,
            "open": float,
            "high": float,
            "low": float,
            "prev_close": float,
        }
        or {"error": str}
    """
    try:
        _rate_limit()
        data = _finnhub_client.quote(symbol)
        if not data or data.get("c", 0) == 0:
            raise ValueError("Empty Finnhub quote response")
        return {
            "symbol": symbol,
            "current_price": data["c"],
            "open": data["o"],
            "high": data["h"],
            "low": data["l"],
            "prev_close": data["pc"],
        }
    except Exception as finnhub_err:
        # ---- yfinance fallback ----
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            return {
                "symbol": symbol,
                "current_price": float(info.last_price),
                "open": float(info.open),
                "high": float(info.day_high),
                "low": float(info.day_low),
                "prev_close": float(info.previous_close),
            }
        except Exception as yf_err:
            return {"error": f"Finnhub: {finnhub_err} | yfinance: {yf_err}"}


# ---------------------------------------------------------------------------
# RSI
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def get_rsi(symbol: str, period: int = 14) -> dict:
    """
    Calculate RSI-{period} for *symbol* using Finnhub candles.
    Falls back to yfinance price history if Finnhub fails.

    Returns:
        {"symbol": str, "RSI": float}
        or {"error": str}
    """
    try:
        _rate_limit()
        now = int(datetime.now().timestamp())
        past = int((datetime.now() - timedelta(days=120)).timestamp())
        res = _finnhub_client.stock_candles(symbol, "D", past, now)
        if res.get("s") != "ok" or not res.get("c"):
            raise ValueError("Bad Finnhub candle response")
        closes = pd.Series(res["c"])
    except Exception:
        # ---- yfinance fallback ----
        try:
            closes = yf.download(symbol, period="6mo", progress=False)["Close"].squeeze()
            if closes.empty:
                return {"error": f"No price data for {symbol}"}
        except Exception as e:
            return {"error": str(e)}

    # Wilder RSI
    delta = closes.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_series = 100 - (100 / (1 + rs))
    rsi_value = float(round(rsi_series.iloc[-1], 2))
    return {"symbol": symbol, "RSI": rsi_value}


# ---------------------------------------------------------------------------
# MACD
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def get_macd(symbol: str) -> dict:
    """
    Calculate MACD (12, 26, 9) for *symbol*.

    Returns:
        {"symbol": str, "MACD": float, "MACD_signal": float}
        or {"error": str}
    """
    try:
        _rate_limit()
        now = int(datetime.now().timestamp())
        past = int((datetime.now() - timedelta(days=200)).timestamp())
        res = _finnhub_client.stock_candles(symbol, "D", past, now)
        if res.get("s") != "ok" or not res.get("c"):
            raise ValueError("Bad Finnhub candle response")
        closes = pd.Series(res["c"])
    except Exception:
        try:
            closes = yf.download(symbol, period="12mo", progress=False)["Close"].squeeze()
            if closes.empty:
                return {"error": f"No price data for {symbol}"}
        except Exception as e:
            return {"error": str(e)}

    ema12 = closes.ewm(span=12, adjust=False).mean()
    ema26 = closes.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return {
        "symbol": symbol,
        "MACD": float(round(macd_line.iloc[-1], 4)),
        "MACD_signal": float(round(signal_line.iloc[-1], 4)),
    }


# ---------------------------------------------------------------------------
# Price history (used by risk_agent and Dashboard)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def get_price_history(symbol: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch OHLCV price history using yfinance (unlimited, no quota).

    Args:
        symbol: Ticker string.
        period: yfinance period string, e.g. "1y", "6mo".

    Returns:
        DataFrame with columns [Open, High, Low, Close, Volume]
        or empty DataFrame on error.
    """
    try:
        df = yf.download(symbol, period=period, progress=False)
        if df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return pd.DataFrame()
