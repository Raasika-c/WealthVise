# agents/risk_agent.py  —  Member 1 (M1)
# Produces the risk_agent output schema consumed by M2's explain_agent,
# M3's strategy_agent, and M4's UI.

# 1. Standard library
# (none)

# 2. Third-party
import numpy as np

# 3. Internal
from utils.data_fetcher import get_price_history


def risk_agent(symbol: str) -> dict:
    """
    Calculate risk metrics for a given stock symbol using 1-year price history.

    Risk level rules (from FRAMEWORK.md Section 6):
        annual_volatility > 40%  → High
        annual_volatility > 20%  → Medium
        else                     → Low

    Returns dict matching the risk_agent schema in FRAMEWORK.md Section 3:
    {
        "symbol": str,
        "annual_volatility": float,   # percentage
        "VaR_95_daily": float,        # percentage (negative = loss)
        "risk_level": "Low" | "Medium" | "High",
        "volatility_contribution": float,  # 0–100
    }
    """
    df = get_price_history(symbol, period="1y")

    if df.empty:
        return {"error": f"No price history available for {symbol}"}

    try:
        # Daily log returns
        closes = df["Close"].squeeze().dropna()
        if len(closes) < 20:
            return {"error": f"Insufficient price data for {symbol}"}

        daily_returns = closes.pct_change().dropna()

        # Annualised volatility (252 trading days)
        annual_vol = float(round(daily_returns.std() * np.sqrt(252) * 100, 2))

        # VaR 95% daily (5th percentile of daily returns → loss figure)
        var_95 = float(round(np.percentile(daily_returns, 5) * 100, 2))

        # Risk level
        if annual_vol > 40:
            risk_level = "High"
        elif annual_vol > 20:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # volatility_contribution mirrors annual_vol (capped at 100)
        volatility_contribution = min(annual_vol, 100.0)

        return {
            "symbol": symbol,
            "annual_volatility": annual_vol,
            "VaR_95_daily": var_95,
            "risk_level": risk_level,
            "volatility_contribution": round(volatility_contribution, 2),
        }

    except Exception as e:
        return {"error": f"Risk calculation failed: {str(e)}"}
