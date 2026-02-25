from playwright.sync_api import sync_playwright
import os
import time

def crawl_xiaohongshu():
    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, "xiaohongshu_titles.txt")

    with sync_playwright() as p:
        # Launch headed browser (headless=False)
        print("Starting browser...")
        browser = p.chromium.launch(headless=False, args=['--start-maximized']) # Maximize window for better visibility
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        url = "https://www.xiaohongshu.com/explore?channel_id=homefeed_recommend"
        print(f"Visiting: {url}")
        page.goto(url)

        # Xiaohongshu may require login or CAPTCHA; pause for manual confirmation or page load
        print("-" * 50)
        print("Please complete the following in the browser (if needed):")
        print("1. Log in (if required)")
        print("2. Solve CAPTCHA")
        print("3. Wait for homepage content to load")
        print("-" * 50)
        
        # Simple wait or manual confirmation
        # page.wait_for_selector(".feed-container", timeout=60000) # Try auto-wait; use input to block if selector is uncertain
        input(">>> Press Enter to continue scraping after page loads... <<<")

        print("Starting scroll-and-scrape...")
        
        # Store all scraped data, using (author, title) as key for deduplication
        # Format: {(author, title): {"y": y, "x": x, "content": entry}}
        unique_items = {}
        
        scroll_counts = 10  # Number of scrolls
        
        for i in range(scroll_counts):
            print(f"Scroll-scraping {i+1}/{scroll_counts}...")
            
            # Scrape content in and near the current viewport
            footers = page.locator(".footer").all()
            
            for footer in footers:
                try:
                    # Get position info (may fail if element is invisible or recycled)
                    box = footer.bounding_box()
                    if not box:
                        continue
                    
                    # Extract title
                    title = "No title"
                    title_el = footer.locator(".title").first
                    if title_el.count() > 0:
                        title = title_el.inner_text().strip()
                    
                    # Extract author
                    author = "Unknown author"
                    author_el = footer.locator(".author .name").first
                    if author_el.count() > 0:
                        author = author_el.inner_text().strip()
                    else:
                        wrapper = footer.locator(".author-wrapper").first
                        if wrapper.count() > 0:
                            author = wrapper.inner_text().strip().split('\n')[0]

                    if title and author:
                        key = (author, title)
                        if key not in unique_items:
                            entry = f"{author}：{title}"
                            unique_items[key] = {
                                "y": box["y"],
                                "x": box["x"],
                                "content": entry
                            }
                except:
                    continue # Ignore individual errors to keep the overall flow

            # Scroll action
            # screenshot_path = os.path.join(output_dir, f"screenshot_{i+1}.png")
            # page.screenshot(path=screenshot_path)
            # print(f"Screenshot saved: {screenshot_path}")

            page.mouse.wheel(0, 1000)
            time.sleep(1.5) # Wait for new content to load
        
        # Convert to list and sort
        items_list = list(unique_items.values())
        # Sort by y (top to bottom), x (left to right)
        items_list.sort(key=lambda item: (int(item["y"] // 10), item["x"]))
        
        results = [item["content"] for item in items_list]
        print(f"Scraping complete! Extracted {len(results)} unique items")

        # Save to file
        with open(output_file, "w", encoding="utf-8") as f:
            for item in results:
                f.write(item + "\n")
        
        print(f"Results saved to: {output_file}")
        
        # Wait for user confirmation before closing, for comparison
        print("-" * 50)
        input(">>> Scraping complete! You can now compare with browser content.\n>>> Press Enter to close the browser...")
        browser.close()

if __name__ == "__main__":
    crawl_xiaohongshu()

