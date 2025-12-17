import requests
from bs4 import BeautifulSoup
import time
import random
from pathlib import Path

# 更新 Headers，增加更多伪装信息
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://movie.douban.com/",
    "Host": "movie.douban.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
}

# 输出目录：固定“相对脚本所在目录”，避免你从不同工作目录运行导致写到别处
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
out_file = OUTPUT_DIR / "douban_top250.txt"
print(f"输出文件: {out_file.resolve()}")

# 打开文件准备写入，使用 utf-8 编码防止中文乱码
with out_file.open("w", encoding="utf-8") as f:
    for n in range(0, 250, 25):
        print(f"正在爬取第 {n//25 + 1} 页...")
        try:
            # 添加超时设置
            response = requests.get(f"https://movie.douban.com/top250?start={n}", headers=headers, timeout=10)
            
            if not response.ok:
                print(f"请求失败: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            all_titles = soup.find_all("span", class_="title")
            
            for title in all_titles:
                if title.string and "/" not in title.string:
                    print(title.string)
                    # 写入文件，记得加换行符
                    f.write(title.string + "\n")
            
            # 随机延时 2 到 5 秒，防止被封
            sleep_time = random.uniform(2, 5)
            print(f"暂停 {sleep_time:.2f} 秒...")
            time.sleep(sleep_time)
                    
        except requests.exceptions.RequestException as e:
            print(f"发生错误: {e}")
            break

