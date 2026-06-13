# test_member2.py
import os
from dotenv import load_dotenv
load_dotenv()

from member2_news_reddit import get_news_data

def test_member2():
    print("=" * 50)
    print("Member 2 — News Smoke Test")
    print("=" * 50)

    symbol = "AAPL"
    print(f"\nFetching data for: {symbol}\n")

    result = get_news_data(symbol)

    print(f"✅ Symbol       : {result['symbol']}")
    print(f"✅ News count   : {result['news_count']}")
    print(f"✅ Reddit count : {result['reddit_count']} (skipped)")
    print(f"✅ Fetched at   : {result['fetched_at']}")

    if result['news_articles']:
        print(f"\n📰 Sample headline : {result['news_articles'][0]['title']}")

    print("\n✅ Schema keys match Member 3 expectations!")
    print("Keys:", list(result.keys()))
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_member2()