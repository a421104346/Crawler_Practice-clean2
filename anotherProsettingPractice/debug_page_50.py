import requests
from bs4 import BeautifulSoup
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

url = "https://prosettings.net/games/cs2/page/50/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    print(f"请求: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # 保存 HTML
        debug_file = "anotherProsettingPractice/output/debug_page_50.html"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"HTML 已保存到 {debug_file}")

        soup = BeautifulSoup(response.text, "html.parser")
        
        # 计数
        links = soup.select("div.player_heading-wrapper h4 a")
        print(f"找到 {len(links)} 个选手链接:")
        for i, link in enumerate(links):
            print(f"{i+1}. {link.get_text(strip=True)}")
            
        # 尝试查找所有的 h4，看看是否漏掉了没有 wrapper 的
        all_h4_links = soup.select("h4 a")
        print(f"\n检查所有 h4 a 标签数量: {len(all_h4_links)}")
            
    else:
        print(f"请求失败: {response.status_code}")

except Exception as e:
    print(f"错误: {e}")
