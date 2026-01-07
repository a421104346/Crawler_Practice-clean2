from playwright.sync_api import sync_playwright
import sys
import os
import time

# 设置标准输出编码为 utf-8
sys.stdout.reconfigure(encoding='utf-8')

url = "https://prosettings.net/games/cs2/page/50/"

try:
    with sync_playwright() as p:
        print(f"正在启动可见的浏览器...")
        # 【修改点】headless=False 表示显示浏览器界面
        browser = p.chromium.launch(headless=False, slow_mo=50) 
        page = browser.new_page()
        
        print(f"正在请求: {url}")
        page.goto(url, timeout=60000)
        
        # 等待内容加载
        print("页面已打开，请观察屏幕上的浏览器窗口...")
        page.wait_for_selector("div.player_heading-wrapper", timeout=30000)
        
        print("正在模拟滚动...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(5) # 多停几秒让你看清楚
        
        # 获取所有选手名字
        player_names = page.eval_on_selector_all(
            "div.player_heading-wrapper h4 a", 
            "elements => elements.map(e => e.textContent.trim())"
        )
        
        print(f"脚本在页面上找到了 {len(player_names)} 个选手:")
        for i, name in enumerate(player_names):
            print(f"{i+1}. {name}")
            
        print("\n如果不关闭窗口，10秒后自动关闭...")
        time.sleep(10)
        browser.close()

except Exception as e:
    print(f"发生错误: {e}")
