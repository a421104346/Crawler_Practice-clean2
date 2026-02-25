from playwright.sync_api import sync_playwright
import sys
import os
import time

# Set stdout encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

url = "https://prosettings.net/games/cs2/page/50/"

try:
    with sync_playwright() as p:
        print(f"Starting visible browser...")
        # headless=False shows the browser UI
        browser = p.chromium.launch(headless=False, slow_mo=50) 
        page = browser.new_page()
        
        print(f"Requesting: {url}")
        page.goto(url, timeout=60000)
        
        # Wait for content to load
        print("Page opened, observe the browser window on screen...")
        page.wait_for_selector("div.player_heading-wrapper", timeout=30000)
        
        print("Simulating scrolling...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(5) # Pause for a few seconds for observation
        
        # Get all player names
        player_names = page.eval_on_selector_all(
            "div.player_heading-wrapper h4 a", 
            "elements => elements.map(e => e.textContent.trim())"
        )
        
        print(f"Script found {len(player_names)} players on the page:")
        for i, name in enumerate(player_names):
            print(f"{i+1}. {name}")
            
        print("\nWindow will auto-close in 10 seconds...")
        time.sleep(10)
        browser.close()

except Exception as e:
    print(f"Error occurred: {e}")
