import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 配置 Matplotlib 中文字体 (Windows)
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
        """抓取单个页面"""
        url = f"{self.base_url}?start={start}"
        try:
            print(f"正在抓取: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"请求失败: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"请求异常: {e}")
            return None

    def parse_page(self, html):
        """解析 HTML 提取电影信息"""
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("div", class_="item")
        
        for item in items:
            # 1. 标题
            title = item.find("span", class_="title").get_text()
            
            # 2. 评分
            rating = item.find("span", class_="rating_num").get_text()
            
            # 3. 评价人数 (例如 "123456人评价")
            star_div = item.find("div", class_="star")
            people_text = star_div.find_all("span")[-1].get_text()
            people_count = re.sub(r'\D', '', people_text) # 只保留数字
            
            # 4. 年份 (位于 bd p 标签的一堆文本中)
            info_text = item.find("div", class_="bd").p.get_text()
            # 常见的格式: "导演: xxx... 1994 / 美国 / ..."
            # 使用正则提取第一个看起来像年份的 4 位数字
            year_match = re.search(r'\d{4}', info_text)
            year = year_match.group() if year_match else "Unknown"

            self.data.append({
                "title": title,
                "rating": float(rating),
                "people_count": int(people_count) if people_count else 0,
                "year": int(year) if year != "Unknown" else None
            })

    def run(self, max_pages=10):
        """执行爬虫流程"""
        print(">>> 开始爬取豆瓣 Top250...")
        for i in range(max_pages):
            start = i * 25
            html = self.fetch_page(start)
            if html:
                self.parse_page(html)
                # 随机等待防止封号
                time.sleep(random.uniform(1, 3))
            else:
                print("页面抓取失败，停止后续任务")
                break
        print(f">>> 爬取完成，共获取 {len(self.data)} 条数据")
        return self.data

def analyze_and_visualize(data, output_dir):
    """数据分析与可视化"""
    if not data:
        print("没有数据可分析")
        return

    df = pd.DataFrame(data)
    
    # 保存原始数据
    csv_path = output_dir / "douban_top250.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"数据已保存至: {csv_path}")

    # --- 分析 1: 年份分布 (按年代) ---
    # 去除没有年份的数据
    df_year = df.dropna(subset=['year']).copy()
    # 计算年代 (例如 1994 -> 1990)
    df_year['decade'] = (df_year['year'] // 10) * 10
    decade_counts = df_year['decade'].value_counts().sort_index()

    print("\n--- 年代分布 ---")
    print(decade_counts)

    # 绘图: 年代分布
    plt.figure(figsize=(10, 6))
    decade_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('豆瓣 Top250 电影年代分布')
    plt.xlabel('年代')
    plt.ylabel('电影数量')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    
    img_path_decade = output_dir / "decade_distribution.png"
    plt.savefig(img_path_decade)
    print(f"年代分布图已保存: {img_path_decade}")
    plt.close()

    # --- 分析 2: 评分分布 ---
    print("\n--- 评分统计 ---")
    print(df['rating'].describe())

    # 绘图: 评分直方图
    plt.figure(figsize=(10, 6))
    plt.hist(df['rating'], bins=10, range=(8, 10), color='salmon', edgecolor='black', alpha=0.7)
    plt.title('豆瓣 Top250 电影评分分布')
    plt.xlabel('评分')
    plt.ylabel('电影数量')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    img_path_rating = output_dir / "rating_distribution.png"
    plt.savefig(img_path_rating)
    print(f"评分分布图已保存: {img_path_rating}")
    plt.close()

if __name__ == "__main__":
    # 设置输出目录
    BASE_DIR = Path(__file__).resolve().parent
    OUTPUT_DIR = BASE_DIR / "output"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 爬取
    scraper = DoubanScraper()
    # 爬取 10 页 (即 Top 250 全量)
    movie_data = scraper.run(max_pages=10)

    # 2. 分析与绘图
    analyze_and_visualize(movie_data, OUTPUT_DIR)
