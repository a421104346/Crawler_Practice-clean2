"""
Xiaohongshu crawler (Playwright)
"""
from backend.core.base_crawler import BaseCrawler
import logging
import sys
from playwright.async_api import async_playwright
import datetime
import asyncio

logger = logging.getLogger(__name__)


class RednoteCrawler(BaseCrawler):
    """Xiaohongshu homepage recommendation crawler"""
    
    def __init__(self):
        super().__init__(use_fake_ua=True)
        self.url = "https://www.xiaohongshu.com/explore?channel_id=homefeed_recommend"
        
    async def run(self, progress_callback=None) -> dict:
        """
        Execute scraping with retry mechanism
        """
        running_loop = asyncio.get_running_loop()
        if sys.platform == "win32":
            return await asyncio.to_thread(self._run_in_new_loop, progress_callback, running_loop)
        return await self._run_internal(progress_callback)

    def _run_in_new_loop(self, progress_callback, main_loop: asyncio.AbstractEventLoop) -> dict:
        """
        Execute in new event loop (Windows compatibility)
        """
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        if loop.__class__.__name__ != "ProactorEventLoop":
            raise RuntimeError("Windows loop is not ProactorEventLoop")

        async def thread_progress(progress: int, message: str):
            if not progress_callback:
                return
            future = asyncio.run_coroutine_threadsafe(progress_callback(progress, message), main_loop)
            await asyncio.wrap_future(future)

        try:
            return loop.run_until_complete(
                self._run_internal(thread_progress if progress_callback else None)
            )
        finally:
            loop.close()

    async def _run_internal(self, progress_callback=None) -> dict:
        """
        Actual scraping logic
        """
        logger.info("Starting Rednote crawler...")
        
        items = []
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if progress_callback:
                    await progress_callback(5, f"Launching browser (attempt {attempt + 1}/{max_retries})...")
                
                async with async_playwright() as p:
                    # Launch browser
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        viewport={'width': 1920, 'height': 1080}
                    )
                    page = await context.new_page()
                    
                    try:
                        if progress_callback:
                            await progress_callback(10, "Accessing Xiaohongshu...")
                        
                        await page.goto(self.url, timeout=30000)
                        
                        # Wait for loading
                        if progress_callback:
                            await progress_callback(20, "Waiting for page to load...")
                        
                        try:
                            # Wait for feed container or footer
                            await page.wait_for_selector('.footer', timeout=15000)
                        except:
                            logger.warning("Timeout waiting for content, trying to scroll anyway")
                        
                        # Scroll and scrape
                        unique_items = {}
                        scroll_steps = 10
                        
                        for step in range(scroll_steps):
                            if progress_callback:
                                progress = 20 + int((step / scroll_steps) * 60)
                                await progress_callback(progress, f"Scrolling and scraping (step {step+1})...")
                            
                            footers = await page.locator(".footer").all()
                            
                            for footer in footers:
                                try:
                                    title_el = footer.locator(".title").first
                                    title = "No title"
                                    if await title_el.count() > 0:
                                        title = await title_el.inner_text()
                                        
                                    author_el = footer.locator(".author .name").first
                                    author = "Unknown author"
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
                        await progress_callback(10, f"Error occurred, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    if progress_callback:
                        await progress_callback(90, f"Final failure: {str(e)}")
                
        if progress_callback:
            await progress_callback(100, "Done!")
            
        return {
            "total": len(items),
            "items": items
        }
