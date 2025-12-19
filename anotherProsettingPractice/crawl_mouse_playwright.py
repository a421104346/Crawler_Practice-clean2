from playwright.sync_api import sync_playwright
import sys
import os
import concurrent.futures
import csv
import time
import random

# 设置标准输出编码为 utf-8
sys.stdout.reconfigure(encoding='utf-8')

input_file = os.path.join(os.path.dirname(__file__), "output", "cs2_players_list.txt")
output_file = os.path.join(os.path.dirname(__file__), "output", "cs2_players_mice_playwright.csv")

if not os.path.exists(input_file):
    print(f"错误: 找不到输入文件 {input_file}")
    sys.exit(1)

with open(input_file, "r", encoding="utf-8") as f:
    players = [line.strip() for line in f if line.strip()]

# 限制并发数：根据你的硬件配置 (96GB RAM + Ultra 7 CPU)，可以提高并发
# 推荐: 10-15 个并发，每个浏览器大约消耗 500MB-1GB 内存
MAX_WORKERS = 20  # 你可以根据实际情况调整到 15-20 

fieldnames = ["Player", "Mouse Name", "DPI", "Sensitivity", "eDPI", "Zoom Sensitivity", "Hz", "Windows Sensitivity"]

def process_player_batch(player_batch, worker_id):
    """每个线程/进程启动一个独立的浏览器实例，处理一批选手"""
    results = []
    
    try:
        with sync_playwright() as p:
            # 启动有头浏览器
            # 每个 worker 都会弹出一个浏览器窗口
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            for player_name in player_batch:
                try:
                    url_name = player_name.lower().replace(" ", "-")
                    url = f"https://prosettings.net/players/{url_name}/#cs2_mouse"
                    
                    page.goto(url, timeout=30000)
                    
                    # 尝试等待鼠标区域加载
                    try:
                        page.wait_for_selector("#cs2_mouse", timeout=5000)
                    except:
                        # 如果超时，可能是没有该部分或者加载慢，继续尝试解析
                        pass
                    
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
                    
                    # 1. 提取鼠标名称
                    # 优先看图片 alt
                    if page.query_selector("#cs2_mouse img"):
                        img_alt = page.eval_on_selector("#cs2_mouse img", "el => el.alt")
                        if img_alt:
                            result["Mouse Name"] = img_alt
                    
                    # 备选：提取 h4
                    if result["Mouse Name"] == "N/A" and page.query_selector("#cs2_mouse h4"):
                        h4_text = page.eval_on_selector("#cs2_mouse h4", "el => el.innerText")
                        if h4_text:
                            result["Mouse Name"] = h4_text

                    # 2. 提取表格数据
                    # 使用 evaluate 执行 JS 提取所有行数据，效率更高
                    table_data = page.evaluate("""() => {
                        const rows = document.querySelectorAll('#cs2_mouse table.settings tr');
                        const data = {};
                        rows.forEach(row => {
                            const th = row.querySelector('th');
                            const td = row.querySelector('td');
                            if (th && td) {
                                data[th.innerText.trim()] = td.innerText.trim();
                            }
                        });
                        return data;
                    }""")
                    
                    if table_data:
                        result["DPI"] = table_data.get("DPI", "N/A")
                        result["Sensitivity"] = table_data.get("Sensitivity", "N/A")
                        result["eDPI"] = table_data.get("eDPI", "N/A")
                        result["Zoom Sensitivity"] = table_data.get("Zoom Sensitivity", "N/A")
                        result["Hz"] = table_data.get("Hz", "N/A")
                        result["Windows Sensitivity"] = table_data.get("Windows Sensitivity", "N/A")
                    
                    print(f"[Worker {worker_id}] {player_name}: {result['Mouse Name']} (Sens: {result['Sensitivity']})")
                    results.append(result)
                    
                except Exception as e:
                    print(f"[Worker {worker_id}] Error processing {player_name}: {e}")
                    results.append({"Player": player_name, "Mouse Name": "Error"})
                
                # 随机休息，避免太快
                time.sleep(random.uniform(1, 2))
                
            browser.close()
            
    except Exception as e:
        print(f"[Worker {worker_id}] Browser crashed: {e}")
        
    return results

def chunk_list(lst, n):
    """将列表分成 n 份"""
    return [lst[i::n] for i in range(n)]

if __name__ == "__main__":
    print(f"开始有头浏览器多线程抓取...")
    print(f"总选手: {len(players)}, 并发数: {MAX_WORKERS}")
    
    # 将任务分配给不同的 worker
    batches = chunk_list(players, MAX_WORKERS)
    
    # 写入表头
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for i, batch in enumerate(batches):
            if batch:
                # 提交任务
                futures.append(executor.submit(process_player_batch, batch, i+1))
        
        # 收集结果并写入
        with open(output_file, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            for future in concurrent.futures.as_completed(futures):
                results = future.result()
                writer.writerows(results)
                f.flush()
                
    print("全部完成！")
