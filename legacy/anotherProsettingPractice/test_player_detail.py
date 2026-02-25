import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Select a test target
test_url = "https://prosettings.net/players/zywoo/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    print(f"Testing direct request: {test_url}")
    response = requests.get(test_url, headers=headers, timeout=10)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to get some key info, e.g. mouse model
        # This is just an example; specific selectors may need adjustment
        title = soup.find('h1')
        print(f"Page title: {title.get_text(strip=True) if title else 'Title not found'}")
        
        # Check for anti-scraping notices
        if "Attention Required" in response.text or "Cloudflare" in response.text:
            print("Warning: Cloudflare verification appears to have been triggered!")
        else:
            print("Success: Page appears to be normal HTML, can be parsed directly!")
            
    else:
        print("Request failed")

except Exception as e:
    print(f"Error occurred: {e}")
