from playwright.sync_api import sync_playwright
import time
import csv
import os
from datetime import datetime

def crawl_weibo_hot_search():
    with sync_playwright() as p:
        # Generate timestamp for this run
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Launch browser with headless=False to see browser actions for debugging
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Target URL - directly pointing to hot search tab
        url = "https://weibo.com/newlogin?tabtype=search&gid=&openLoginLayer=0&url=https%3A%2F%2Fwww.weibo.com%2F"
        
        print(f"Visiting: {url}")
        page.goto(url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        # Increase wait time to ensure virtual list loading completes
        time.sleep(5)

        # Store all unique scraped items, using item_key as key to avoid duplicates
        all_items = {}
        target_count = 50
        
        # Try scroll-based scraping
        # Virtual lists usually require scrolling to load subsequent content
        # Perform multiple scrolls, scraping visible elements after each scroll
        for scroll_step in range(15): # Try more scrolls to ensure coverage
            print(f"Scrolling step {scroll_step+1}...")
            
            # Get currently visible list items
            items = page.locator('.vue-recycle-scroller__item-view')
            count = items.count()
            print(f"Currently visible: {count} items")

            for i in range(count):
                item = items.nth(i)
                text_content = item.inner_text().strip()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                
                if not lines:
                    continue

                # Extract rank and title
                # Text structure usually contains: rank, title, tag (New/Hot), heat value
                numbers = []
                title_candidates = []
                
                # Try to find link
                link = ""
                link_el = item.locator('a')
                if link_el.count() > 0:
                     link = link_el.first.get_attribute('href')
                     if link and not link.startswith('http'):
                        link = f"https:{link}"

                for line in lines:
                    if line.isdigit():
                        numbers.append(int(line))
                    elif len(line) > 1 and "热" not in line and "新" != line and "爆" != line and "商" != line and "Top" != line:
                        title_candidates.append(line)

                real_rank = 1000 # Default large rank, placed at end when sorting
                hot_value = 0
                title = title_candidates[0] if title_candidates else ""
                
                # Distinguish rank from heat value
                if len(numbers) >= 2:
                    numbers.sort()
                    real_rank = numbers[0] # Smaller value is rank
                    hot_value = numbers[-1] # Larger value is heat
                elif len(numbers) == 1:
                    val = numbers[0]
                    if val <= 100: # Assume rank won't exceed 100
                        real_rank = val
                    else:
                        hot_value = val
                
                # Special handling for Top
                if "Top" in lines:
                    real_rank = 0
                
                # Skip if no valid title found
                if not title:
                    continue

                # Use title as key to prevent duplicates (rank parsing may be inaccurate)
                item_key = f"{real_rank}_{title}"
                
                if item_key not in all_items:
                    # Only add when valid info is captured
                    print(f"Found: Rank {real_rank}, Hot {hot_value}, Title {title}")
                    all_items[item_key] = {
                        'rank': real_rank, 
                        'hot_value': hot_value,
                        'title': title, 
                        'link': link,
                        'crawl_time': current_time
                    }
            
            # Check if target count reached (only counting valid ranks)
            valid_items = [i for i in all_items.values() if i['rank'] <= 100]
            if len(valid_items) >= target_count:
                print("Collected enough items")
                break
                
            # Scroll the page
            page.mouse.wheel(0, 800) 
            time.sleep(1.5)

        # Organize results: sort by rank
        # Sort by rank first; if tied (both 1000), sort by hot_value descending
        sorted_results = sorted(all_items.values(), key=lambda x: (x['rank'], -x['hot_value']))
        
        print(f"Total items collected: {len(sorted_results)}")

        # Save results
        output_dir = 'weibo/output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save timestamped file to preserve history
        csv_file = f'{output_dir}/weibo_hot_search_{file_timestamp}.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['rank', 'title', 'hot_value', 'link', 'crawl_time'])
            writer.writeheader()
            writer.writerows(sorted_results)
            
        print(f"Results saved to {csv_file}")
        
        browser.close()

if __name__ == "__main__":
    crawl_weibo_hot_search()
