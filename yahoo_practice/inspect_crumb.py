import requests
from fake_useragent import UserAgent
import re

# 1. 设置 Session 以保持 Cookie
session = requests.Session()
# 使用桌面浏览器的 UA，因为移动端页面结构可能不同
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
session.headers.update(header)

print(">>> Step 1: Visiting a Yahoo Finance page to get Cookies...")
url = 'https://finance.yahoo.com/quote/AAPL'

try:
    response = session.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    # 查看获取到的 Cookies
    cookies = session.cookies.get_dict()
    print(f"Cookies collected: {list(cookies.keys())}")
    
    if 'A3' in cookies or 'B' in cookies:
         print("Looks good! We got the main Yahoo cookies.")
    
    # 2. 尝试在 HTML 中寻找 Crumb
    # 历史经验：Yahoo 经常把 Crumb 放在 window.YAHOO.context.crumb 或者类似的 JS 变量里
    print("\n>>> Step 2: Searching for Crumb in HTML...")
    
    # 常见的 Crumb 模式
    patterns = [
        r'"CrumbStore":\{"crumb":"(.*?)"\}',
        r'"crumb":"(.*?)"',
        r'crumb: "(.*?)"'
    ]
    
    found = False
    for pattern in patterns:
        matches = re.findall(pattern, response.text)
        if matches:
            print(f"Found potential crumbs with pattern '{pattern}':")
            # 打印前3个避免刷屏，且只打印前20字符
            for m in matches[:3]:
                print(f"  - {m}")
            found = True
            # break # Don't break, let's see all matches for debugging
            
    if not found:
        print("No obvious crumb found in HTML. They might be fetching it via a separate API call now.")
        # 保存 HTML 以便手动检查（如果需要）
        with open("yahoo_practice/debug_yahoo.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved HTML to 'yahoo_practice/debug_yahoo.html' for inspection.")

except Exception as e:
    print(f"Error: {e}")

