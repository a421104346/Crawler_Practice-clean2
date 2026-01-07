import requests
import sys
import os
import csv
from bs4 import BeautifulSoup

# 设置标准输出编码为 utf-8，防止 Windows 终端乱码
sys.stdout.reconfigure(encoding='utf-8')

# 确保输出目录存在
output_dir = r"D:\projects\WebCrawler\prosetting\output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"创建目录: {output_dir}")

url = "https://prosettings.net/lists/cs2/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

output_file = os.path.join(output_dir, "cs2_prosettings.csv")
html_debug_file = os.path.join(output_dir, "source_debug.html")

try:
    print(f"正在请求: {url}")
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        # 保存原始 HTML 用于调试
        with open(html_debug_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"原始 HTML 已保存到: {html_debug_file}")

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找表格
        table = soup.find('table', id='pro-list-table')
        
        if table:
            # 提取表头
            headers_list = []
            thead = table.find('thead')
            if thead:
                th_tags = thead.find_all('th')
                headers_list = [th.get_text(strip=True) for th in th_tags]
            
            # 提取数据行
            rows_data = []
            tbody = table.find('tbody')
            if tbody:
                tr_tags = tbody.find_all('tr')
                print(f"DEBUG: tbody 中共有 {len(tr_tags)} 个 tr 标签")
                for i, tr in enumerate(tr_tags):
                    td_tags = tr.find_all('td')
                    row = [td.get_text(strip=True) for td in td_tags]
                    if row: # 确保不是空行
                        rows_data.append(row)
                    else:
                        print(f"DEBUG: 第 {i+1} 个 tr 是空行或没有 td")
            
            print(f"解析后找到 {len(rows_data)} 行有效数据。")
            
            if rows_data:
                # 写入 CSV
                with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    if headers_list:
                        writer.writerow(headers_list)
                    writer.writerows(rows_data)
                print(f"数据已成功保存到: {output_file}")
            else:
                print("未找到表格数据行，可能需要检查页面结构或反爬策略。")
                
        else:
            print("未找到 ID 为 'pro-list-table' 的表格。")
    else:
        print(f"请求失败，状态码不是 200。")
        
except Exception as e:
    print(f"发生错误: {e}")
