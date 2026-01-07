from yahoo_crawler import YahooCrawler

# 实例化一次，自动处理所有脏活（获取 Cookie，获取 Crumb，伪装 UA）
print("Starting Crawler Bot...")
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
            market_time = meta['regularMarketTime']
            
            print(f"[OK] {symbol} Price: {price} {currency}")
            
        except Exception as e:
            print(f"[ERROR] Failed to parse data for {symbol}: {e}")
    else:
        print(f"[ERROR] Failed to fetch {symbol}")

print("\nDone! The delay is automatically controlled to simulate human rhythm.")

