import requests
from fake_useragent import UserAgent

# 1. 初始化 Session
session = requests.Session()

# 必须使用非常标准的 PC 浏览器 UA，Yahoo 对 UA 校验很严格
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1'
}
session.headers.update(headers)

print(">>> Step 1: Visiting Homepage to initialize session/cookies...")
# 有时候访问 fcc 页面更能强制设置 cookie
# 但通常主页就够了
homepage_url = 'https://finance.yahoo.com' 

try:
    resp = session.get(homepage_url, timeout=10)
    print(f"Homepage Status: {resp.status_code}")
    print(f"Cookies after homepage: {list(session.cookies.get_dict().keys())}")
    
    # 2. 尝试从 API 获取 Crumb
    print("\n>>> Step 2: Fetching Crumb from API...")
    crumb_url = 'https://query1.finance.yahoo.com/v1/test/getcrumb'
    
    # 注意：请求 Crumb 时，Referer 很重要
    crumb_headers = {
        'Referer': homepage_url
    }
    
    resp_crumb = session.get(crumb_url, headers=crumb_headers, timeout=10)
    print(f"Crumb API Status: {resp_crumb.status_code}")
    
    crumb = resp_crumb.text
    print(f"Crumb Value: '{crumb}'")
    
    if resp_crumb.status_code == 200 and crumb:
        print("\n>>> Step 3: SUCCESS! Now fetching AAPL data with Crumb...")
        quote_url = f"https://query1.finance.yahoo.com/v8/finance/chart/AAPL?symbol=AAPL&crumb={crumb}"
        
        resp_quote = session.get(quote_url, timeout=10)
        print(f"Quote API Status: {resp_quote.status_code}")
        
        if resp_quote.status_code == 200:
            data = resp_quote.json()
            try:
                meta = data['chart']['result'][0]['meta']
                print(f"Price: {meta['regularMarketPrice']} {meta['currency']}")
            except:
                 print(f"Data structure might have changed: {str(data)[:100]}")
        else:
            print(f"Failed to get quote. Response: {resp_quote.text[:100]}")
    else:
        print("Failed to get crumb. Maybe IP blocked or header mismatch.")

except Exception as e:
    print(f"Error: {e}")

