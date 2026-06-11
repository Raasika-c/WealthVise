# agents/market_agent.py  —  Member 1 (M1)
# Produces the market_agent output schema consumed by M3 and M2.

# 1. Standard library
# (none needed beyond what utils imports)

# 2. Third-party
import streamlit as st

# 3. Internal
from utils.data_fetcher import get_quote, get_rsi, get_macd


def market_analysis_agent(symbol: str) -> dict:
    """
    Analyse the market trend for a given stock symbol.

    RSI rules (from FRAMEWORK.md Section 6):
        RSI > 70  → Bearish (overbought)
        RSI < 30  → Bullish (oversold)
        else      → Neutral

    rsi_contribution = abs(RSI - 50) / 50 * 100

    Returns dict matching the market_agent schema in FRAMEWORK.md Section 3:
    {
        "symbol": str,
        "RSI": float,
        "MACD": float,
        "MACD_signal": float,
        "trend": "Bullish" | "Bearish" | "Neutral",
        "recommendation": "BUY" | "SELL" | "HOLD",
        "rsi_contribution": float,
    }
    """
    # ---- Fetch data -------------------------------------------------------
    rsi_data = get_rsi(symbol)
    macd_data = get_macd(symbol)

    # Propagate errors early
    if "error" in rsi_data:
        return {"error": f"RSI fetch failed: {rsi_data['error']}"}
    if "error" in macd_data:
        return {"error": f"MACD fetch failed: {macd_data['error']}"}

    rsi: float = rsi_data["RSI"]
    macd: float = macd_data["MACD"]
    macd_signal: float = macd_data["MACD_signal"]

    # ---- Trend & recommendation -------------------------------------------
    if rsi > 70:
        trend = "Bearish"
        recommendation = "SELL"
    elif rsi < 30:
        trend = "Bullish"
        recommendation = "BUY"
    else:
        trend = "Neutral"
        # Use MACD crossover to refine the neutral case
        if macd > macd_signal:
            recommendation = "BUY"
        elif macd < macd_signal:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"

    # ---- RSI contribution ------------------------------------------------
    rsi_contribution = round(abs(rsi - 50) / 50 * 100, 2)

    return {
        "symbol": symbol,
        "RSI": rsi,
        "MACD": macd,
        "MACD_signal": macd_signal,
        "trend": trend,
        "recommendation": recommendation,
        "rsi_contribution": rsi_contribution,
    }
