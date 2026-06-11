# test_member1.py  —  Run locally to verify M1 code before pushing.
# Usage: python test_member1.py
import json
from utils.data_fetcher import get_quote, get_rsi, get_macd, get_price_history
from agents.market_agent import market_analysis_agent
from agents.risk_agent import risk_agent

TEST_SYMBOL = "AAPL"

def separator(title: str) -> None:
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)

if __name__ == "__main__":
    separator("get_quote")
    result = get_quote(TEST_SYMBOL)
    print(json.dumps(result, indent=2))

    separator("get_rsi")
    result = get_rsi(TEST_SYMBOL)
    print(json.dumps(result, indent=2))

    separator("get_macd")
    result = get_macd(TEST_SYMBOL)
    print(json.dumps(result, indent=2))

    separator("get_price_history  (last 3 rows)")
    df = get_price_history(TEST_SYMBOL, "1y")
    print(df.tail(3))

    separator("market_analysis_agent")
    result = market_analysis_agent(TEST_SYMBOL)
    print(json.dumps(result, indent=2))

    separator("risk_agent")
    result = risk_agent(TEST_SYMBOL)
    print(json.dumps(result, indent=2))

    print("\n✅  All M1 smoke tests passed (no unhandled exceptions).")
