import requests
from bs4 import BeautifulSoup
import sys
import os

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
        print("=== 找到 mouse_section ===")
        # 根据截图，表格直接在 mouse_section 下面，或者在 div.promo 下面
        # 我们先查找所有 table
        tables = mouse_section.find_all("table")
        print(f"找到 {len(tables)} 个表格")
        
        for idx, table in enumerate(tables):
            print(f"\n--- 表格 {idx+1} ---")
            print(f"Class: {table.get('class')}")
            
            # 尝试提取每一行
            rows = table.find_all("tr")
            for row in rows:
                # 根据截图，tr 上有 data-field 属性，例如 data-field="dpi"
                data_field = row.get("data-field")
                
                # 单元格内容
                cols = row.find_all("td")
                # 截图里好像只有两个 td，一个是 Label 没显示出来？或者它是 th?
                # 让我们打印一下 row 的完整内容看看结构
                print(f"Row data-field='{data_field}': {row.get_text(strip=True)}")
                print(row.prettify()[:200]) # 打印一些 HTML 看看结构

    else:
        print("未找到 id='cs2_mouse'")

except Exception as e:
    print(e)
