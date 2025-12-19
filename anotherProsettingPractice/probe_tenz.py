import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://prosettings.net/players/tenz/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找 id="cs2_mouse"
    mouse_section = soup.find(id="cs2_mouse")
    if mouse_section:
        print("=== ID 'cs2_mouse' Content Start ===")
        # 打印前 2000 个字符，应该能看到表格结构
        print(mouse_section.prettify()[:2000])
        print("=== ID 'cs2_mouse' Content End ===")
        
        # 尝试查找里面的所有表格
        tables = mouse_section.find_all("table")
        print(f"\n找到 {len(tables)} 个表格在鼠标区域内。")
        for i, table in enumerate(tables):
            print(f"表格 {i+1} class: {table.get('class')}")
            print(table.prettify()[:500]) # 打印表格前几行
            
    else:
        print("未找到 id='cs2_mouse'")

except Exception as e:
    print(e)
