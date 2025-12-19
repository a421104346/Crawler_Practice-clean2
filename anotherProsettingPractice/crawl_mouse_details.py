import requests
from bs4 import BeautifulSoup
import sys
import os
import concurrent.futures
import csv
import time
import random

# 设置标准输出编码为 utf-8
sys.stdout.reconfigure(encoding='utf-8')

# 配置文件路径
input_file = os.path.join(os.path.dirname(__file__), "output", "cs2_players_list.txt")
output_file = os.path.join(os.path.dirname(__file__), "output", "cs2_players_mice_detailed.csv")

# 确保输入文件存在
if not os.path.exists(input_file):
    print(f"错误: 找不到输入文件 {input_file}")
    sys.exit(1)

# 读取选手名单
with open(input_file, "r", encoding="utf-8") as f:
    players = [line.strip() for line in f if line.strip()]

print(f"读取到 {len(players)} 名选手。")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 目标字段 (移除 Status)
fieldnames = ["Player", "Mouse Name", "DPI", "Sensitivity", "eDPI", "Zoom Sensitivity", "Hz", "Windows Sensitivity"]

def crawl_player_mouse_details(player_name):
    url_name = player_name.lower().replace(" ", "-")
    url = f"https://prosettings.net/players/{url_name}/"
    
    result = {
        "Player": player_name,
        "Mouse Name": "N/A",
        "DPI": "N/A",
        "Sensitivity": "N/A",
        "eDPI": "N/A",
        "Zoom Sensitivity": "N/A",
        "Hz": "N/A",
        "Windows Sensitivity": "N/A"
    }
    
    try:
        time.sleep(random.uniform(0.1, 0.3))
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找 id="cs2_mouse"
            mouse_section = soup.find(id="cs2_mouse")
            if mouse_section:
                # 1. 查找鼠标名称
                img = mouse_section.find("img")
                if img and img.get("alt"):
                    result["Mouse Name"] = img.get("alt")
                else:
                    # 如果没有图片，尝试查找 h4
                    h4 = mouse_section.find("h4")
                    if h4:
                        result["Mouse Name"] = h4.get_text(strip=True)
                
                # 2. 查找表格并提取参数
                # 根据 probe 结果，表格行是 tr -> th(Key) + td(Value)
                settings_table = mouse_section.find("table", class_="settings")
                if settings_table:
                    rows = settings_table.find_all("tr")
                    for row in rows:
                        th = row.find("th")
                        td = row.find("td")
                        
                        if th and td:
                            key = th.get_text(strip=True)
                            value = td.get_text(strip=True)
                            
                            if key == "DPI":
                                result["DPI"] = value
                            elif key == "Sensitivity":
                                result["Sensitivity"] = value
                            elif key == "eDPI":
                                result["eDPI"] = value
                            elif key == "Zoom Sensitivity":
                                result["Zoom Sensitivity"] = value
                            elif key == "Hz":
                                result["Hz"] = value
                            elif key == "Windows Sensitivity":
                                result["Windows Sensitivity"] = value
            
            return result
            
        else:
            # 即使出错也返回空数据结构
            return result
            
    except Exception:
        # 即使出错也返回空数据结构
        return result

print(f"开始抓取详细鼠标参数，使用 20 个线程...")
print(f"结果将保存到: {output_file}")

# 写入表头
with open(output_file, "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

total_done = 0
max_workers = 20

with open(output_file, "a", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_player = {executor.submit(crawl_player_mouse_details, player): player for player in players}
        
        for future in concurrent.futures.as_completed(future_to_player):
            try:
                data = future.result()
                writer.writerow(data)
                csvfile.flush()
                
                total_done += 1
                if total_done % 10 == 0:
                    print(f"进度: {total_done}/{len(players)} - {data['Player']}: DPI={data['DPI']}, Sens={data['Sensitivity']}")
                    
            except Exception as exc:
                print(f"异常: {exc}")

print("抓取完成！")
