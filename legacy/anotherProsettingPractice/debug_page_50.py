import requests
from bs4 import BeautifulSoup
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

url = "https://prosettings.net/games/cs2/page/50/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    print(f"Requesting: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # Save HTML
        debug_file = "anotherProsettingPractice/output/debug_page_50.html"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"HTML saved to {debug_file}")

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Count results
        links = soup.select("div.player_heading-wrapper h4 a")
        print(f"Found {len(links)} player links:")
        for i, link in enumerate(links):
            print(f"{i+1}. {link.get_text(strip=True)}")
            
        # Try finding all h4 tags to check if any without wrapper are missed
        all_h4_links = soup.select("h4 a")
        print(f"\nChecking all h4 a tag count: {len(all_h4_links)}")
            
    else:
        print(f"Request failed: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
