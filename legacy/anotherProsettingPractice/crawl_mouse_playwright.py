from playwright.sync_api import sync_playwright
import sys
import os
import concurrent.futures
import csv
import time
import random

# Set stdout encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

input_file = os.path.join(os.path.dirname(__file__), "output", "cs2_players_list.txt")
output_file = os.path.join(os.path.dirname(__file__), "output", "cs2_players_mice_playwright.csv")

if not os.path.exists(input_file):
    print(f"Error: Input file not found {input_file}")
    sys.exit(1)

with open(input_file, "r", encoding="utf-8") as f:
    players = [line.strip() for line in f if line.strip()]

# Limit concurrency: based on hardware (96GB RAM + Ultra 7 CPU), can increase concurrency
# Recommended: 10-15 concurrent, each browser uses ~500MB-1GB RAM
MAX_WORKERS = 20  # Adjust to 15-20 based on actual conditions

fieldnames = ["Player", "Mouse Name", "DPI", "Sensitivity", "eDPI", "Zoom Sensitivity", "Hz", "Windows Sensitivity"]

def process_player_batch(player_batch, worker_id):
    """Each thread/process launches an independent browser instance to process a batch of players"""
    results = []
    
    try:
        with sync_playwright() as p:
            # Launch headed browser
            # Each worker opens a browser window
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            for player_name in player_batch:
                try:
                    url_name = player_name.lower().replace(" ", "-")
                    url = f"https://prosettings.net/players/{url_name}/#cs2_mouse"
                    
                    page.goto(url, timeout=30000)
                    
                    # Try to wait for mouse section to load
                    try:
                        page.wait_for_selector("#cs2_mouse", timeout=5000)
                    except:
                        # If timeout, section may not exist or is loading slowly; continue parsing
                        pass
                    
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
                    
                    # 1. Extract mouse name
                    # Prefer image alt
                    if page.query_selector("#cs2_mouse img"):
                        img_alt = page.eval_on_selector("#cs2_mouse img", "el => el.alt")
                        if img_alt:
                            result["Mouse Name"] = img_alt
                    
                    # Fallback: extract h4
                    if result["Mouse Name"] == "N/A" and page.query_selector("#cs2_mouse h4"):
                        h4_text = page.eval_on_selector("#cs2_mouse h4", "el => el.innerText")
                        if h4_text:
                            result["Mouse Name"] = h4_text

                    # 2. Extract table data
                    # Use evaluate to run JS for all row data, more efficient
                    table_data = page.evaluate("""() => {
                        const rows = document.querySelectorAll('#cs2_mouse table.settings tr');
                        const data = {};
                        rows.forEach(row => {
                            const th = row.querySelector('th');
                            const td = row.querySelector('td');
                            if (th && td) {
                                data[th.innerText.trim()] = td.innerText.trim();
                            }
                        });
                        return data;
                    }""")
                    
                    if table_data:
                        result["DPI"] = table_data.get("DPI", "N/A")
                        result["Sensitivity"] = table_data.get("Sensitivity", "N/A")
                        result["eDPI"] = table_data.get("eDPI", "N/A")
                        result["Zoom Sensitivity"] = table_data.get("Zoom Sensitivity", "N/A")
                        result["Hz"] = table_data.get("Hz", "N/A")
                        result["Windows Sensitivity"] = table_data.get("Windows Sensitivity", "N/A")
                    
                    print(f"[Worker {worker_id}] {player_name}: {result['Mouse Name']} (Sens: {result['Sensitivity']})")
                    results.append(result)
                    
                except Exception as e:
                    print(f"[Worker {worker_id}] Error processing {player_name}: {e}")
                    results.append({"Player": player_name, "Mouse Name": "Error"})
                
                # Random sleep to avoid being too fast
                time.sleep(random.uniform(1, 2))
                
            browser.close()
            
    except Exception as e:
        print(f"[Worker {worker_id}] Browser crashed: {e}")
        
    return results

def chunk_list(lst, n):
    """Split list into n chunks"""
    return [lst[i::n] for i in range(n)]

if __name__ == "__main__":
    print(f"Starting multi-threaded headed browser scraping...")
    print(f"Total players: {len(players)}, concurrency: {MAX_WORKERS}")
    
    # Distribute tasks to different workers
    batches = chunk_list(players, MAX_WORKERS)
    
    # Write headers
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for i, batch in enumerate(batches):
            if batch:
                # Submit tasks
                futures.append(executor.submit(process_player_batch, batch, i+1))
        
        # Collect results and write
        with open(output_file, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            for future in concurrent.futures.as_completed(futures):
                results = future.result()
                writer.writerows(results)
                f.flush()
                
    print("All done!")
