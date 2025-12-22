from playwright.sync_api import sync_playwright
import time
import csv
import os
from datetime import datetime

def crawl_weibo_hot_search():
    with sync_playwright() as p:
        # Generate timestamp for this run
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 启动浏览器，headless=False 可以看到浏览器操作过程，方便调试
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 目标 URL - 直接指向热搜 Tab
        url = "https://weibo.com/newlogin?tabtype=search&gid=&openLoginLayer=0&url=https%3A%2F%2Fwww.weibo.com%2F"
        
        print(f"正在访问: {url}")
        page.goto(url)
        
        # 等待页面加载
        print("等待页面加载...")
        # 增加等待时间，确保虚拟列表加载完成
        time.sleep(5)

        # 存储所有抓取到的唯一条目，使用 item_key 作为 key 避免重复
        all_items = {}
        target_count = 50
        
        # 尝试滚动抓取
        # 虚拟列表通常需要滚动才能加载后续内容
        # 我们进行多次滚动，每次滚动后抓取当前可见的元素
        for scroll_step in range(15): # 尝试滚动更多次以确保覆盖
            print(f"Scrolling step {scroll_step+1}...")
            
            # 获取当前可见的列表项
            items = page.locator('.vue-recycle-scroller__item-view')
            count = items.count()
            print(f"当前可见 {count} 个条目")

            for i in range(count):
                item = items.nth(i)
                text_content = item.inner_text().strip()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                
                if not lines:
                    continue

                # 提取排名和标题
                # 文本结构通常包含：排名、标题、标签(新/热)、热度
                numbers = []
                title_candidates = []
                
                # 尝试查找链接
                link = ""
                link_el = item.locator('a')
                if link_el.count() > 0:
                     link = link_el.first.get_attribute('href')
                     if link and not link.startswith('http'):
                        link = f"https:{link}"

                for line in lines:
                    if line.isdigit():
                        numbers.append(int(line))
                    elif len(line) > 1 and "热" not in line and "新" != line and "爆" != line and "商" != line and "Top" != line:
                        title_candidates.append(line)

                real_rank = 1000 # 默认一个较大的排名，用于排序放到后面
                hot_value = 0
                title = title_candidates[0] if title_candidates else ""
                
                # 区分排名和热度
                if len(numbers) >= 2:
                    numbers.sort()
                    real_rank = numbers[0] # 较小的是排名
                    hot_value = numbers[-1] # 较大的是热度
                elif len(numbers) == 1:
                    val = numbers[0]
                    if val <= 100: # 假设排名不会超过 100
                        real_rank = val
                    else:
                        hot_value = val
                
                # 特殊处理 Top
                if "Top" in lines:
                    real_rank = 0
                
                # 如果没有找到有效标题，跳过
                if not title:
                    continue

                # 使用 title 作为 key 防止重复 (因为 rank 可能解析不准)
                item_key = f"{real_rank}_{title}"
                
                if item_key not in all_items:
                    # 只有当我们认为抓到了有效信息时才添加
                    print(f"Found: Rank {real_rank}, Hot {hot_value}, Title {title}")
                    all_items[item_key] = {
                        'rank': real_rank, 
                        'hot_value': hot_value,
                        'title': title, 
                        'link': link,
                        'crawl_time': current_time
                    }
            
            # 检查是否已达到目标数量 (仅计算有效排名的)
            valid_items = [i for i in all_items.values() if i['rank'] <= 100]
            if len(valid_items) >= target_count:
                print("已收集到足够的条目")
                break
                
            # 滚动页面
            page.mouse.wheel(0, 800) 
            time.sleep(1.5)

        # 整理结果：按排名排序
        # 首先按 rank 排序，如果 rank 相同（都是1000），则按 hot_value 降序
        sorted_results = sorted(all_items.values(), key=lambda x: (x['rank'], -x['hot_value']))
        
        print(f"总共收集到 {len(sorted_results)} 个条目")

        # 保存结果
        output_dir = 'weibo/output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 保存带时间戳的文件，保留历史记录
        csv_file = f'{output_dir}/weibo_hot_search_{file_timestamp}.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['rank', 'title', 'hot_value', 'link', 'crawl_time'])
            writer.writeheader()
            writer.writerows(sorted_results)
            
        print(f"结果已保存到 {csv_file}")
        
        browser.close()

if __name__ == "__main__":
    crawl_weibo_hot_search()
