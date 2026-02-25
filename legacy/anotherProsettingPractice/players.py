from playwright.sync_api import sync_playwright
import time
import os
import sys
import random

# Set stdout encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(__file__), "output")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, "cs2_players_list.txt")

def run():
    print(f"Starting scrape, results will be saved to: {output_file}")
    
    with sync_playwright() as p:
        # headless=False: Show browser to bypass simple anti-scraping
        print("Starting browser...")
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        total_players = 0
        
        # Use write mode to start fresh; append mode could preserve previous data
        # Since we're re-scraping, use 'w' to rewrite, or we could only re-scrape failed pages
        # For simplicity, run a full scrape with retry logic for failed pages
        
        # Implement a simple retry mechanism
        
        with open(output_file, "w", encoding="utf-8") as f:
            for page_num in range(1, 51):
                if page_num == 1:
                    url = "https://prosettings.net/games/cs2/"
                else:
                    url = f"https://prosettings.net/games/cs2/page/{page_num}/"
                
                print(f"Scraping page {page_num}: {url}")
                
                max_retries = 3
                success = False
                
                for attempt in range(max_retries):
                    try:
                        # Visit page
                        page.goto(url, timeout=60000)
                        
                        # Wait for key elements to load
                        page.wait_for_selector("div.player_heading-wrapper", timeout=15000)
                        
                        # Simulate scrolling to trigger lazy loading
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(1) # Brief wait for post-scroll loading
                        
                        # Get all players on this page
                        names = page.eval_on_selector_all(
                            "div.player_heading-wrapper h4 a", 
                            "elements => elements.map(e => e.textContent.trim())"
                        )
                        
                        if names:
                            count = 0
                            for name in names:
                                if name:
                                    f.write(name + "\n")
                                    count += 1
                            
                            total_players += count
                            print(f"  -> Found {count} players on page {page_num}")
                            f.flush()
                            success = True
                            break # Success, exit retry loop
                        else:
                            print(f"  -> No data found on page {page_num} (attempt {attempt+1}/{max_retries})")

                    except Exception as e:
                        print(f"  -> Error on page {page_num} (attempt {attempt+1}/{max_retries}): {e}")
                        time.sleep(3) # Wait longer after error
                
                if not success:
                    print(f"  ❌ Gave up on page {page_num}, scraping failed.")

                # Random delay
                time.sleep(random.uniform(1.0, 2.0))
        
        print(f"\nScraping complete! Total players scraped: {total_players}.")
        browser.close()

if __name__ == "__main__":
    run()
