import requests
from bs4 import BeautifulSoup
import sys

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
        print("=== ID 'cs2_mouse' Content Start ===")
        # Print first 2000 chars to see table structure
        print(mouse_section.prettify()[:2000])
        print("=== ID 'cs2_mouse' Content End ===")
        
        # Try to find all tables inside
        tables = mouse_section.find_all("table")
        print(f"\nFound {len(tables)} tables in the mouse section.")
        for i, table in enumerate(tables):
            print(f"Table {i+1} class: {table.get('class')}")
            print(table.prettify()[:500]) # Print first few rows of the table
            
    else:
        print("id='cs2_mouse' not found")

except Exception as e:
    print(e)
