import requests
from fake_useragent import UserAgent
import re

# 1. Set up Session to maintain cookies
session = requests.Session()
# Use desktop browser UA since mobile page structure may differ
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
session.headers.update(header)

print(">>> Step 1: Visiting a Yahoo Finance page to get Cookies...")
url = 'https://finance.yahoo.com/quote/AAPL'

try:
    response = session.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    # Check the collected cookies
    cookies = session.cookies.get_dict()
    print(f"Cookies collected: {list(cookies.keys())}")
    
    if 'A3' in cookies or 'B' in cookies:
         print("Looks good! We got the main Yahoo cookies.")
    
    # 2. Try to find Crumb in HTML
    # Historical note: Yahoo often stores Crumb in window.YAHOO.context.crumb or similar JS variables
    print("\n>>> Step 2: Searching for Crumb in HTML...")
    
    # Common Crumb patterns
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
            # Print first 3 to avoid flooding output
            for m in matches[:3]:
                print(f"  - {m}")
            found = True
            # break # Don't break, let's see all matches for debugging
            
    if not found:
        print("No obvious crumb found in HTML. They might be fetching it via a separate API call now.")
        # Save HTML for manual inspection (if needed)
        with open("yahoo_practice/debug_yahoo.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved HTML to 'yahoo_practice/debug_yahoo.html' for inspection.")

except Exception as e:
    print(f"Error: {e}")

