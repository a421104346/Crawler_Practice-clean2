from playwright.sync_api import sync_playwright
import os
import time

def crawl_xiaohongshu():
    # 确保输出目录存在
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, "xiaohongshu_titles.txt")

    with sync_playwright() as p:
        # 启动有头浏览器 (headless=False)
        print("正在启动浏览器...")
        browser = p.chromium.launch(headless=False, args=['--start-maximized']) # 最大化窗口以便查看
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        url = "https://www.xiaohongshu.com/explore?channel_id=homefeed_recommend"
        print(f"正在访问: {url}")
        page.goto(url)

        # 小红书可能需要登录或者有验证码，这里暂停等待人工确认或页面加载
        print("-" * 50)
        print("请在浏览器中完成以下操作（如果需要）：")
        print("1. 登录账号 (如果是必须的)")
        print("2. 解决验证码")
        print("3. 等待首页内容加载完成")
        print("-" * 50)
        
        # 简单等待或人工确认
        # page.wait_for_selector(".feed-container", timeout=60000) # 尝试自动等待，如果不确定选择器，可以用 input 阻塞
        input(">>> 页面加载完成后，请按回车键继续抓取... <<<")

        print("开始边滚动边抓取...")
        
        # 存储所有抓取到的数据，使用 (author, title) 作为 key 去重
        # 格式: {(author, title): {"y": y, "x": x, "content": entry}}
        unique_items = {}
        
        scroll_counts = 10  # 滚动次数
        
        for i in range(scroll_counts):
            print(f"正在进行第 {i+1}/{scroll_counts} 次滚动抓取...")
            
            # 抓取当前视口及附近的内容
            footers = page.locator(".footer").all()
            
            for footer in footers:
                try:
                    # 获取位置信息（如果元素不可见或被回收，可能获取不到 box）
                    box = footer.bounding_box()
                    if not box:
                        continue
                    
                    # 提取标题
                    title = "无标题"
                    title_el = footer.locator(".title").first
                    if title_el.count() > 0:
                        title = title_el.inner_text().strip()
                    
                    # 提取作者
                    author = "未知作者"
                    author_el = footer.locator(".author .name").first
                    if author_el.count() > 0:
                        author = author_el.inner_text().strip()
                    else:
                        wrapper = footer.locator(".author-wrapper").first
                        if wrapper.count() > 0:
                            author = wrapper.inner_text().strip().split('\n')[0]

                    if title and author:
                        key = (author, title)
                        if key not in unique_items:
                            entry = f"{author}：{title}"
                            unique_items[key] = {
                                "y": box["y"],
                                "x": box["x"],
                                "content": entry
                            }
                except:
                    continue # 忽略单条报错，保证整体流程

            # 滚动操作
            # screenshot_path = os.path.join(output_dir, f"screenshot_{i+1}.png")
            # page.screenshot(path=screenshot_path)
            # print(f"已保存截图: {screenshot_path}")

            page.mouse.wheel(0, 1000)
            time.sleep(1.5) # 等待新内容加载
        
        # 转换为列表并排序
        items_list = list(unique_items.values())
        # 按 y (从上到下), x (从左到右) 排序
        items_list.sort(key=lambda item: (int(item["y"] // 10), item["x"]))
        
        results = [item["content"] for item in items_list]
        print(f"抓取完成！去重后共提取到 {len(results)} 条数据")

        # 保存到文件
        with open(output_file, "w", encoding="utf-8") as f:
            for item in results:
                f.write(item + "\n")
        
        print(f"结果已保存至: {output_file}")
        
        # 等待用户确认后再关闭，方便对照
        print("-" * 50)
        input(">>> 抓取完成！现在你可以对照浏览器内容了。\n>>> 按回车键关闭浏览器...")
        browser.close()

if __name__ == "__main__":
    crawl_xiaohongshu()

