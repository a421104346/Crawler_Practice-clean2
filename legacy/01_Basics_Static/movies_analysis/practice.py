import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Configure Matplotlib Chinese font (Windows)
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class DoubanScraper:
    def __init__(self):
        self.base_url = "https://movie.douban.com/top250"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://movie.douban.com/",
        }
        self.data = []

    def fetch_page(self, start):
        """Fetch a single page"""
        url = f"{self.base_url}?start={start}"
        try:
            print(f"Scraping: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Request failed: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None

    def parse_page(self, html):
        """Parse HTML to extract movie info"""
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("div", class_="item")
        
        for item in items:
            # 1. Title
            title = item.find("span", class_="title").get_text()
            
            # 2. Rating
            rating = item.find("span", class_="rating_num").get_text()
            
            # 3. Number of reviews (e.g. "123456人评价")
            # Method: find span tags containing "人评价" text within the item area
            # Content-based targeting is more stable than counting span indices
            people_span = item.find("span", string=re.compile("人评价"))
            if people_span:
                people_count = re.sub(r'\D', '', people_span.get_text())
            else:
                people_count = 0
            
            # 4. Year (within text of bd p tags)
            info_text = item.find("div", class_="bd").p.get_text()
            # Common format: "导演: xxx... 1994 / 美国 / ..."
            # Use regex to extract the first 4-digit number that looks like a year
            year_match = re.search(r'\d{4}', info_text)
            year = year_match.group() if year_match else "Unknown"

            self.data.append({
                "title": title,
                "rating": float(rating),
                "people_count": int(people_count) if people_count else 0,
                "year": int(year) if year != "Unknown" else None
            })

    def run(self, max_pages=10):
        """Execute the scraping workflow"""
        print(">>> Starting Douban Top 250 scrape...")
        for i in range(max_pages):
            start = i * 25
            html = self.fetch_page(start)
            if html:
                self.parse_page(html)
                # Random wait to avoid being banned
                time.sleep(random.uniform(1, 3))
            else:
                print("Page scraping failed, stopping subsequent tasks")
                break
        print(f">>> Scraping complete, collected {len(self.data)} records")
        return self.data

def analyze_and_visualize(data, output_dir):
    """Data analysis and visualization"""
    if not data:
        print("No data to analyze")
        return

    df = pd.DataFrame(data)
    
    # Save raw data
    csv_path = output_dir / "douban_top250.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"Data saved to: {csv_path}")

    # --- Analysis 1: Year distribution (by specific year) ---
    # Remove entries without year data
    df_year = df.dropna(subset=['year']).copy()
    # Count by specific year instead of 10-year buckets
    year_counts = df_year['year'].value_counts().sort_index()

    print("\n--- Year Distribution ---")
    print(year_counts)

    # Plot: Year distribution
    # Many specific years (spanning decades), so use wider chart (figsize=(15, 6))
    plt.figure(figsize=(15, 6))
    year_counts.plot(kind='bar', color='skyblue', edgecolor='black', width=0.8)
    plt.title('Douban Top 250 Movie Year Distribution')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    # Rotate X-axis labels 90 degrees with smaller font to prevent overlap
    plt.xticks(rotation=90, fontsize=8)
    
    # Filename updated to year_distribution.png for distinction
    img_path_year = output_dir / "year_distribution.png"
    plt.savefig(img_path_year)
    print(f"Year distribution chart saved: {img_path_year}")
    plt.close()

    # --- Analysis 2: Rating distribution ---
    print("\n--- Rating Statistics ---")
    print(df['rating'].describe())

    # Plot: Rating histogram
    plt.figure(figsize=(10, 6))
    plt.hist(df['rating'], bins=10, range=(8, 10), color='salmon', edgecolor='black', alpha=0.7)
    plt.title('Douban Top 250 Movie Rating Distribution')
    plt.xlabel('Rating')
    plt.ylabel('Number of Movies')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    img_path_rating = output_dir / "rating_distribution.png"
    plt.savefig(img_path_rating)
    print(f"Rating distribution chart saved: {img_path_rating}")
    plt.close()

if __name__ == "__main__":
    # Set output directory
    BASE_DIR = Path(__file__).resolve().parent
    OUTPUT_DIR = BASE_DIR / "output"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Scrape
    scraper = DoubanScraper()
    # Scrape 10 pages (full Top 250)
    movie_data = scraper.run(max_pages=10)

    # 2. Analyze and plot
    analyze_and_visualize(movie_data, OUTPUT_DIR)
