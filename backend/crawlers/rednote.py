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
        执行爬取，包含重试机制
        """
        logger.info("Starting Rednote crawler...")
        
        items = []
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if progress_callback:
                    await progress_callback(5, f"启动浏览器 (尝试 {attempt + 1}/{max_retries})...")
                
                async with async_playwright() as p:
                    # 启动浏览器
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        viewport={'width': 1920, 'height': 1080}
                    )
                    page = await context.new_page()
                    
                    try:
                        if progress_callback:
                            await progress_callback(10, "正在访问小红书...")
                        
                        await page.goto(self.url, timeout=30000)
                        
                        # 等待加载
                        if progress_callback:
                            await progress_callback(20, "等待页面加载...")
                        
                        try:
                            # 等待 feed 容器或 footer
                            await page.wait_for_selector('.footer', timeout=15000)
                        except:
                            logger.warning("Timeout waiting for content, trying to scroll anyway")
                        
                        # 滚动抓取
                        unique_items = {}
                        scroll_steps = 10
                        
                        for step in range(scroll_steps):
                            if progress_callback:
                                progress = 20 + int((step / scroll_steps) * 60)
                                await progress_callback(progress, f"正在滚动并抓取 (第 {step+1} 次)...")
                            
                            footers = await page.locator(".footer").all()
                            
                            for footer in footers:
                                try:
                                    title_el = footer.locator(".title").first
                                    title = "无标题"
                                    if await title_el.count() > 0:
                                        title = await title_el.inner_text()
                                        
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
                                    
                            await page.mouse.wheel(0, 1000)
                            await asyncio.sleep(1.5)
                        
                        items = list(unique_items.values())
                        
                        if items:
                            break
                        else:
                            raise Exception("No items found")
                            
                    finally:
                        await context.close()
                        await browser.close()
                        
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    if progress_callback:
                        await progress_callback(10, f"发生错误，{wait_time}秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    if progress_callback:
                        await progress_callback(90, f"最终失败: {str(e)}")
                
        if progress_callback:
            await progress_callback(100, "完成！")
            
        return {
            "total": len(items),
            "items": items
        }
