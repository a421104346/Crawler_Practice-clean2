"""
小红书爬虫 (Playwright)
"""
from backend.core.base_crawler import BaseCrawler
import logging
from playwright.async_api import async_playwright
import datetime
import asyncio

logger = logging.getLogger(__name__)


class RednoteCrawler(BaseCrawler):
    """小红书首页推荐爬虫"""
    
    def __init__(self):
        super().__init__(use_fake_ua=True)
        self.url = "https://www.xiaohongshu.com/explore?channel_id=homefeed_recommend"
        
    async def run(self, progress_callback=None) -> dict:
        """
        执行爬取
        """
        logger.info("Starting Rednote crawler...")
        
        items = []
        
        if progress_callback:
            await progress_callback(5, "正在启动浏览器...")
            
        async with async_playwright() as p:
            # 启动浏览器 (无头模式可能被反爬，这里尝试无头，如果不可以可能需要 headless=False 但服务器环境不支持)
            # 小红书反爬较严，这里仅做基本实现演示
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            try:
                if progress_callback:
                    await progress_callback(10, "正在访问小红书...")
                
                await page.goto(self.url)
                
                # 等待加载
                if progress_callback:
                    await progress_callback(20, "等待页面加载...")
                
                try:
                    # 等待 feed 容器或 footer
                    await page.wait_for_selector('.footer', timeout=15000)
                except:
                    logger.warning("Timeout waiting for content")
                
                # 滚动抓取
                unique_items = {}
                scroll_steps = 10
                
                for step in range(scroll_steps):
                    if progress_callback:
                        progress = 20 + int((step / scroll_steps) * 60)
                        await progress_callback(progress, f"正在滚动并抓取 (第 {step+1} 次)...")
                    
                    # 获取卡片
                    footers = await page.locator(".footer").all()
                    
                    for footer in footers:
                        try:
                            # 提取标题
                            title_el = footer.locator(".title").first
                            title = "无标题"
                            if await title_el.count() > 0:
                                title = await title_el.inner_text()
                                
                            # 提取作者
                            author_el = footer.locator(".author .name").first
                            author = "未知作者"
                            if await author_el.count() > 0:
                                author = await author_el.inner_text()
                                
                            if title and author:
                                key = f"{author}_{title}"
                                if key not in unique_items:
                                    unique_items[key] = {
                                        "title": title.strip(),
                                        "author": author.strip(),
                                        "crawl_time": datetime.datetime.now().isoformat()
                                    }
                        except Exception:
                            continue
                            
                    # 滚动
                    await page.mouse.wheel(0, 1000)
                    await asyncio.sleep(1.5)
                
                items = list(unique_items.values())
                
            except Exception as e:
                logger.error(f"Error during Rednote crawl: {e}", exc_info=True)
                if progress_callback:
                    await progress_callback(90, f"发生错误: {str(e)}")
            finally:
                if progress_callback:
                    await progress_callback(95, "正在关闭浏览器...")
                await context.close()
                await browser.close()
                
        if progress_callback:
            await progress_callback(100, "完成！")
            
        return {
            "total": len(items),
            "items": items
        }
