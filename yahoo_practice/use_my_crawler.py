import sys
import os

# 将项目根目录添加到 python path，这样才能导入 core 和 crawlers 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.yahoo import YahooCrawler

# 实例化一次，自动处理所有脏活（获取 Cookie，获取 Crumb，伪装 UA）
print("Starting Crawler Bot (Refactored)...")
bot = YahooCrawler()

stocks = ['AAPL', 'MSFT', 'NVDA', 'TSLA']

print("\nBatch fetching started...")
for symbol in stocks:
    print(f"\nFetching {symbol}...")
    data = bot.get_quote(symbol)
    
    if data:
        try:
            # 解析 Yahoo 返回的复杂 JSON 结构
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
