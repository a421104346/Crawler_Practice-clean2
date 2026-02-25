import sys
import os

# Add project root to python path so core and crawlers modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.yahoo import YahooCrawler

# Instantiate once, automatically handles all dirty work (get Cookie, get Crumb, fake UA)
print("Starting Crawler Bot (Refactored)...")
bot = YahooCrawler()

stocks = ['AAPL', 'MSFT', 'NVDA', 'TSLA']

print("\nBatch fetching started...")
for symbol in stocks:
    print(f"\nFetching {symbol}...")
    data = bot.get_quote(symbol)
    
    if data:
        try:
            # Parse Yahoo's complex JSON response structure
            result = data['chart']['result'][0]
            meta = result['meta']
            price = meta['regularMarketPrice']
            currency = meta['currency']
            
            print(f"[OK] {symbol} Price: {price} {currency}")
            
        except Exception as e:
            print(f"[ERROR] Failed to parse data for {symbol}: {e}")
    else:
        print(f"[ERROR] Failed to fetch {symbol}")

print("\nDone! The delay is automatically controlled to simulate human rhythm.")
