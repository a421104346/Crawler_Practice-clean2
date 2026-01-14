"""
微博热搜爬虫 (Playwright)
"""
from backend.core.base_crawler import BaseCrawler
import logging
from playwright.async_api import async_playwright
import datetime
import asyncio

logger = logging.getLogger(__name__)


class WeiboCrawler(BaseCrawler):
    """微博热搜爬虫"""
    
    def __init__(self):
        # Playwright 不需要 httpx 的 base_delay，但保留父类初始化
        super().__init__(use_fake_ua=True)
        self.url = "https://weibo.com/newlogin?tabtype=search&gid=&openLoginLayer=0&url=https%3A%2F%2Fwww.weibo.com%2F"
        
    async def run(self, progress_callback=None) -> dict:
        """
        执行爬取
        """
        logger.info("Starting Weibo crawler...")
        
        items = []
        
        if progress_callback:
            await progress_callback(5, "正在启动浏览器...")
            
        async with async_playwright() as p:
            # 启动浏览器 (无头模式)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            try:
                if progress_callback:
                    await progress_callback(10, "正在访问微博热搜...")
                
                await page.goto(self.url)
                
                # 等待加载
                if progress_callback:
                    await progress_callback(20, "等待页面加载...")
                
                # 等待列表元素出现
                try:
                    await page.wait_for_selector('.vue-recycle-scroller__item-view', timeout=10000)
                except:
                    logger.warning("Timeout waiting for scroller items")
                
                # 滚动抓取
                all_items_dict = {}
                target_count = 50
                scroll_steps = 10
                
                for step in range(scroll_steps):
                    if progress_callback:
                        progress = 20 + int((step / scroll_steps) * 60)
                        await progress_callback(progress, f"正在滚动并抓取 (第 {step+1} 次)...")
                    
                    # 获取当前可见条目
                    elements = await page.locator('.vue-recycle-scroller__item-view').all()
                    
                    for el in elements:
                        try:
                            text = await el.inner_text()
                            lines = [l.strip() for l in text.split('\n') if l.strip()]
                            
                            if not lines:
                                continue
                                
                            # 简单解析逻辑 (参考 legacy)
                            # 通常格式: 排名 标题 热度
                            rank = 1000
                            title = ""
                            hot_value = 0
                            
                            # 尝试提取链接
                            link = ""
                            link_el = el.locator('a').first
                            if await link_el.count() > 0:
                                href = await link_el.get_attribute('href')
                                if href:
                                    link = href if href.startswith('http') else f"https:{href}"
                            
                            # 解析文本行
                            nums = []
                            candidates = []
                            for line in lines:
                                if line.isdigit():
                                    nums.append(int(line))
                                elif len(line) > 1 and line not in ["热", "新", "爆", "商", "Top"]:
                                    candidates.append(line)
                            
                            if candidates:
                                title = candidates[0]
                                
                            if len(nums) >= 2:
                                nums.sort()
                                rank = nums[0]
                                hot_value = nums[-1]
                            elif len(nums) == 1:
                                val = nums[0]
                                if val <= 50:
                                    rank = val
                                else:
                                    hot_value = val
                                    
                            if "Top" in lines:
                                rank = 0
                                
                            if title:
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
                            
                    # 滚动
                    await page.mouse.wheel(0, 800)
                    await asyncio.sleep(1)
                    
                    # 检查是否足够
                    if len(all_items_dict) >= target_count * 1.5:
                        break
                
                items = list(all_items_dict.values())
                # 排序
                items.sort(key=lambda x: x['rank'])
                
            except Exception as e:
                logger.error(f"Error during Weibo crawl: {e}", exc_info=True)
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
