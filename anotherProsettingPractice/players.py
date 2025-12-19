from playwright.sync_api import sync_playwright
import time
import os
import sys
import random

# 设置标准输出编码为 utf-8
sys.stdout.reconfigure(encoding='utf-8')

# 确保输出目录存在
output_dir = os.path.join(os.path.dirname(__file__), "output")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, "cs2_players_list.txt")

def run():
    print(f"开始抓取，结果将保存到: {output_file}")
    
    with sync_playwright() as p:
        # headless=False: 显示浏览器以绕过简单的反爬虫
        print("正在启动浏览器...")
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        total_players = 0
        
        # 使用追加模式打开文件，以免覆盖之前已抓取的数据（如果想保留）
        # 但既然是重新抓取，这里还是使用 'w' 重新写，或者我们可以只补抓失败的页面
        # 鉴于刚刚第2页失败了，我们单独补抓第2页？
        # 或者为了简单，我建议再运行一次完整的，但是加上对失败页面的重试机制。
        
        # 这里我将实现一个简单的重试逻辑
        
        with open(output_file, "w", encoding="utf-8") as f:
            for page_num in range(1, 51):
                if page_num == 1:
                    url = "https://prosettings.net/games/cs2/"
                else:
                    url = f"https://prosettings.net/games/cs2/page/{page_num}/"
                
                print(f"正在抓取第 {page_num} 页: {url}")
                
                max_retries = 3
                success = False
                
                for attempt in range(max_retries):
                    try:
                        # 访问页面
                        page.goto(url, timeout=60000)
                        
                        # 等待关键元素加载
                        page.wait_for_selector("div.player_heading-wrapper", timeout=15000)
                        
                        # 模拟滚动以触发懒加载
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(1) # 短暂等待滚动后的加载
                        
                        # 获取该页所有选手
                        names = page.eval_on_selector_all(
                            "div.player_heading-wrapper h4 a", 
                            "elements => elements.map(e => e.textContent.trim())"
                        )
                        
                        if names:
                            count = 0
                            for name in names:
                                if name:
                                    f.write(name + "\n")
                                    count += 1
                            
                            total_players += count
                            print(f"  -> 第 {page_num} 页找到 {count} 个选手")
                            f.flush()
                            success = True
                            break # 成功则退出重试循环
                        else:
                            print(f"  -> 第 {page_num} 页未找到数据 (尝试 {attempt+1}/{max_retries})")

                    except Exception as e:
                        print(f"  -> 第 {page_num} 页发生错误 (尝试 {attempt+1}/{max_retries}): {e}")
                        time.sleep(3) # 出错后多等一会
                
                if not success:
                    print(f"  ❌ 放弃第 {page_num} 页，抓取失败。")

                # 随机延时
                time.sleep(random.uniform(1.0, 2.0))
        
        print(f"\n抓取完成！共抓取 {total_players} 个选手。")
        browser.close()

if __name__ == "__main__":
    run()
