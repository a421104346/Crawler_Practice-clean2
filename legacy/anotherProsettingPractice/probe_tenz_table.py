import requests
from bs4 import BeautifulSoup
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

url = "https://prosettings.net/players/tenz/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find id="cs2_mouse"
    mouse_section = soup.find(id="cs2_mouse")
    if mouse_section:
        print("=== Found mouse_section ===")
        # Based on screenshots, the table is directly under mouse_section or under div.promo
        # First find all tables
        tables = mouse_section.find_all("table")
        print(f"Found {len(tables)} tables")
        
        for idx, table in enumerate(tables):
            print(f"\n--- Table {idx+1} ---")
            print(f"Class: {table.get('class')}")
            
            # Try to extract each row
            rows = table.find_all("tr")
            for row in rows:
                # Based on screenshots, tr has data-field attribute, e.g. data-field="dpi"
                data_field = row.get("data-field")
                
                # Cell content
                cols = row.find_all("td")
                # Screenshots show only two td; one may be a Label or th
                # Print row content to see the structure
                print(f"Row data-field='{data_field}': {row.get_text(strip=True)}")
                print(row.prettify()[:200]) # Print some HTML to see the structure

    else:
        print("id='cs2_mouse' not found")

except Exception as e:
    print(e)
