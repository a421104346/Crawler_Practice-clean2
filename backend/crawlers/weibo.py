"""
微博热搜爬虫 (Playwright)
"""
from backend.core.base_crawler import BaseCrawler
import logging
import sys
from playwright.async_api import async_playwright
import datetime
import asyncio

logger = logging.getLogger(__name__)


class WeiboCrawler(BaseCrawler):
    """微博热搜爬虫"""
    
    def __init__(self):
        super().__init__(use_fake_ua=True)
        # 使用公开热搜页，避免登录墙
        self.url = "https://s.weibo.com/top/summary?cate=realtimehot"
        
    async def run(self, progress_callback=None) -> dict:
        """
        执行爬取，包含重试机制
        """
        running_loop = asyncio.get_running_loop()
        if sys.platform == "win32":
            return await asyncio.to_thread(self._run_in_new_loop, progress_callback, running_loop)
        return await self._run_internal(progress_callback)

    def _run_in_new_loop(self, progress_callback, main_loop: asyncio.AbstractEventLoop) -> dict:
        """
        在新事件循环中执行（Windows 兼容性）
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
        实际爬取逻辑
        """
        logger.info("Starting Weibo crawler...")
        
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
                        viewport={'width': 1920, 'height': 1080},
                        locale="zh-CN",
                        timezone_id="Asia/Shanghai",
                        extra_http_headers={
                            "Accept-Language": "zh-CN,zh;q=0.9"
                        }
                    )
                    page = await context.new_page()
                    
                    try:
                        if progress_callback:
                            await progress_callback(10, "正在访问微博热搜...")
                        
                        response = await page.goto(self.url, timeout=30000, wait_until="domcontentloaded")
                        status = response.status if response else None
                        if status and status >= 400:
                            raise Exception(f"Unexpected status code: {status}")
                        
                        # 等待加载
                        if progress_callback:
                            await progress_callback(20, "等待页面加载...")
                        
                        # 等待列表元素出现
                        try:
                            await page.wait_for_selector("#pl_top_realtimehot table tbody tr", timeout=10000)
                        except Exception as e:
                            logger.warning(f"Timeout waiting for hot search table: {e}")
                        
                        page_url = page.url
                        if "login" in page_url or "passport" in page_url:
                            raise Exception("Redirected to login page")
                        
                        content = await page.content()
                        if "访问频次过高" in content or "安全验证" in content or "验证码" in content:
                            raise Exception("Blocked by anti-bot protection")

                        all_items_dict = {}
                        target_count = 50

                        elements = await page.locator("#pl_top_realtimehot table tbody tr").all()
                        if not elements:
                            elements = await page.locator("table tbody tr").all()
                        for el in elements:
                            try:
                                rank_el = el.locator("td.td-01")
                                if await rank_el.count() == 0:
                                    rank_el = el.locator("td.ranktop")
                                rank_text = (await rank_el.inner_text()).strip()

                                title_el = el.locator("td.td-02 a").first
                                hot_el = el.locator("td.td-03").first

                                title = (await title_el.inner_text()).strip()
                                if not title:
                                    continue

                                href = await title_el.get_attribute("href")
                                link = ""
                                if href:
                                    link = href if href.startswith("http") else f"https://s.weibo.com{href}"

                                rank = int(rank_text) if rank_text.isdigit() else 1000

                                hot_value = 0
                                if await hot_el.count() > 0:
                                    hot_text = (await hot_el.inner_text()).strip()
                                    digits = "".join([c for c in hot_text if c.isdigit()])
                                    if digits:
                                        hot_value = int(digits)

                                key = f"{rank}_{title}"
                                if key not in all_items_dict:
                                    all_items_dict[key] = {
                                        "rank": rank,
                                        "title": title,
                                        "hot": hot_value,
                                        "link": link,
                                        "crawl_time": datetime.datetime.now().isoformat()
                                    }
                            except Exception as e:
                                logger.debug(f"Error parsing item: {e}")
                                continue

                            if len(all_items_dict) >= target_count:
                                break
                        
                        items = list(all_items_dict.values())
                        items.sort(key=lambda x: x['rank'])
                        
                        # 如果成功获取数据，退出重试循环
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
                
        if not items:
            raise Exception("No items found after retries")

        if progress_callback:
            await progress_callback(100, "完成！")
            
        return {
            "total": len(items),
            "items": items
        }
