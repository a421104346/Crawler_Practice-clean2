import requests
import sys
import os
import csv
from bs4 import BeautifulSoup

# Set stdout encoding to utf-8 to prevent garbled text on Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

# Ensure output directory exists
output_dir = r"D:\projects\WebCrawler\prosetting\output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

url = "https://prosettings.net/lists/cs2/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

output_file = os.path.join(output_dir, "cs2_prosettings.csv")
html_debug_file = os.path.join(output_dir, "source_debug.html")

try:
    print(f"Requesting: {url}")
    response = requests.get(url, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        # Save raw HTML for debugging
        with open(html_debug_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Raw HTML saved to: {html_debug_file}")

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find table
        table = soup.find('table', id='pro-list-table')
        
        if table:
            # Extract headers
            headers_list = []
            thead = table.find('thead')
            if thead:
                th_tags = thead.find_all('th')
                headers_list = [th.get_text(strip=True) for th in th_tags]
            
            # Extract data rows
            rows_data = []
            tbody = table.find('tbody')
            if tbody:
                tr_tags = tbody.find_all('tr')
                print(f"DEBUG: Found {len(tr_tags)} tr tags in tbody")
                for i, tr in enumerate(tr_tags):
                    td_tags = tr.find_all('td')
                    row = [td.get_text(strip=True) for td in td_tags]
                    if row: # Ensure it's not an empty row
                        rows_data.append(row)
                    else:
                        print(f"DEBUG: tr #{i+1} is empty or has no td")
            
            print(f"Found {len(rows_data)} valid data rows after parsing.")
            
            if rows_data:
                # Write to CSV
                with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    if headers_list:
                        writer.writerow(headers_list)
                    writer.writerows(rows_data)
                print(f"Data saved successfully to: {output_file}")
            else:
                print("No table data rows found. Check page structure or anti-scraping measures.")
                
        else:
            print("Table with ID 'pro-list-table' not found.")
    else:
        print(f"Request failed, status code is not 200.")
        
except Exception as e:
    print(f"Error occurred: {e}")
