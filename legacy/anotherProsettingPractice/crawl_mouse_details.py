import requests
from bs4 import BeautifulSoup
import sys
import os
import concurrent.futures
import csv
import time
import random

# Set stdout encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Configure file paths
input_file = os.path.join(os.path.dirname(__file__), "output", "cs2_players_list.txt")
output_file = os.path.join(os.path.dirname(__file__), "output", "cs2_players_mice_detailed.csv")

# Ensure input file exists
if not os.path.exists(input_file):
    print(f"Error: Input file not found {input_file}")
    sys.exit(1)

# Read player list
with open(input_file, "r", encoding="utf-8") as f:
    players = [line.strip() for line in f if line.strip()]

print(f"Read {len(players)} players.")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Target fields (Status removed)
fieldnames = ["Player", "Mouse Name", "DPI", "Sensitivity", "eDPI", "Zoom Sensitivity", "Hz", "Windows Sensitivity"]

def crawl_player_mouse_details(player_name):
    url_name = player_name.lower().replace(" ", "-")
    url = f"https://prosettings.net/players/{url_name}/"
    
    result = {
        "Player": player_name,
        "Mouse Name": "N/A",
        "DPI": "N/A",
        "Sensitivity": "N/A",
        "eDPI": "N/A",
        "Zoom Sensitivity": "N/A",
        "Hz": "N/A",
        "Windows Sensitivity": "N/A"
    }
    
    try:
        time.sleep(random.uniform(0.1, 0.3))
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find id="cs2_mouse"
            mouse_section = soup.find(id="cs2_mouse")
            if mouse_section:
                # 1. Find mouse name
                img = mouse_section.find("img")
                if img and img.get("alt"):
                    result["Mouse Name"] = img.get("alt")
                else:
                    # If no image, try to find h4
                    h4 = mouse_section.find("h4")
                    if h4:
                        result["Mouse Name"] = h4.get_text(strip=True)
                
                # 2. Find table and extract parameters
                # Based on probe results, table rows are tr -> th(Key) + td(Value)
                settings_table = mouse_section.find("table", class_="settings")
                if settings_table:
                    rows = settings_table.find_all("tr")
                    for row in rows:
                        th = row.find("th")
                        td = row.find("td")
                        
                        if th and td:
                            key = th.get_text(strip=True)
                            value = td.get_text(strip=True)
                            
                            if key == "DPI":
                                result["DPI"] = value
                            elif key == "Sensitivity":
                                result["Sensitivity"] = value
                            elif key == "eDPI":
                                result["eDPI"] = value
                            elif key == "Zoom Sensitivity":
                                result["Zoom Sensitivity"] = value
                            elif key == "Hz":
                                result["Hz"] = value
                            elif key == "Windows Sensitivity":
                                result["Windows Sensitivity"] = value
            
            return result
            
        else:
            # Return empty data structure even on error
            return result
            
    except Exception:
        # Return empty data structure even on error
        return result

print(f"Starting detailed mouse parameter scraping with 20 threads...")
print(f"Results will be saved to: {output_file}")

# Write headers
with open(output_file, "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

total_done = 0
max_workers = 20

with open(output_file, "a", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_player = {executor.submit(crawl_player_mouse_details, player): player for player in players}
        
        for future in concurrent.futures.as_completed(future_to_player):
            try:
                data = future.result()
                writer.writerow(data)
                csvfile.flush()
                
                total_done += 1
                if total_done % 10 == 0:
                    print(f"Progress: {total_done}/{len(players)} - {data['Player']}: DPI={data['DPI']}, Sens={data['Sensitivity']}")
                    
            except Exception as exc:
                print(f"Exception: {exc}")

print("Scraping complete!")
