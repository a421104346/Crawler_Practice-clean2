import requests
from bs4 import BeautifulSoup
import time
import random
from pathlib import Path

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://ph.jobstreet.com/",
    "Connection": "keep-alive",
}

url = "https://ph.jobstreet.com/jobs-in-information-communication-technology"

# Output directory: fixed relative to script location to avoid path issues when running from different working directories
# Just change the last part of OUTPUT_DIR (e.g., change to BASE_DIR / "output" / "xxx")
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output" / "jobstreet"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
print(f"Output directory: {OUTPUT_DIR.resolve()}")

# Random delay to reduce risk of triggering anti-bot measures (no guarantee to bypass 403)
time.sleep(random.uniform(1.5, 3.5))

try:
    with requests.Session() as s:
        resp = s.get(url, headers=headers, timeout=15, allow_redirects=True)
        print(f"Status code: {resp.status_code}")

        if not resp.ok:
            # 403 common: blocked by site anti-bot; save page content for analyzing required headers/cookies
            debug_path = OUTPUT_DIR / "jobstreet_debug.html"
            debug_path.write_text(resp.text, encoding="utf-8")
            print(f"Request failed, response content saved to {debug_path} (for debugging 403/redirect/CAPTCHA).")
            raise SystemExit(1)

        # Save page HTML for writing selectors later (open in browser to see structure)
        page_path = OUTPUT_DIR / "jobstreet_page.html"
        page_path.write_text(resp.text, encoding="utf-8")
        print(f"Page saved to {page_path}")

        # Placeholder parsing: refine extraction after confirming page structure (won't reach here on 403)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else "(no title)"
        print(f"Page title: {title}")
except requests.exceptions.RequestException as e:
    print(f"Network request error: {e}")