import requests
from fake_useragent import UserAgent
import json

# 目标 URL：Yahoo Finance 的 Quote API (获取 AAPL 的基本数据)
# 这个接口比解析 HTML 更直接
url = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"

print(f"Trying to access: {url}\n")

# --- Experiment 1: Direct connection (Usually fails) ---
print(">>> Experiment 1: No User-Agent (Raw)")
try:
    response = requests.get(url, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response snippet: {response.text[:100]}...")
except Exception as e:
    print(f"Error: {e}")

print("-" * 30)

# --- Experiment 2: Fake Browser ---
print(">>> Experiment 2: With User-Agent (Fake Browser)")
ua = UserAgent()
headers = {
    'User-Agent': ua.random
}
print(f"Using User-Agent: {headers['User-Agent']}")

try:
    response = requests.get(url, headers=headers, timeout=5)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        try:
            price = data['chart']['result'][0]['meta']['regularMarketPrice']
            currency = data['chart']['result'][0]['meta']['currency']
            print(f"Success! AAPL Current Price: {price} {currency}")
        except:
            print(f"JSON Parse Failed. Raw data: {str(data)[:200]}")
    else:
        print("Failed even with User-Agent. Crumb might be required.")
        print(f"Response: {response.text[:200]}")

except Exception as e:
    print(f"Error: {e}")

