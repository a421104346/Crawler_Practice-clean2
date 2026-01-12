import httpx
from fake_useragent import UserAgent
import asyncio
import random
import logging
from typing import Optional, Any

# 配置日志，方便看到爬虫在干什么
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

class BaseCrawler:
    def __init__(self, use_fake_ua=True, base_delay=1.0, progress_callback=None):
        """
        初始化爬虫基类
        :param use_fake_ua: 是否自动使用随机 User-Agent
        :param base_delay: 每次请求的基础延时(秒)，实际延时会在 0.5x ~ 1.5x 之间浮动
        :param progress_callback: 进度回调函数 fn(progress: int, message: str)
        """
        self.base_delay = base_delay
        self.progress_callback = progress_callback
        self.use_fake_ua = use_fake_ua
        
        # 初始化 headers
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if use_fake_ua:
            self._rotate_ua()
        else:
            # 默认给一个稳健的 Chrome UA
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            
        # 创建异步客户端
        self.client = httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=30.0)

    def _rotate_ua(self):
        """随机切换 User-Agent"""
        try:
            ua = UserAgent()
            self.headers['User-Agent'] = ua.random
            logging.info(f"User-Agent switched to: {self.headers['User-Agent'][:50]}...")
            # 如果 client 已经存在，更新 headers
            if hasattr(self, 'client'):
                self.client.headers.update({'User-Agent': self.headers['User-Agent']})
        except Exception as e:
            logging.warning(f"Failed to generate fake UA, using default. Error: {e}")

    async def _sleep(self):
        """智能延时：模拟人类操作的随机停顿"""
        if self.base_delay > 0:
            # 随机波动 +/- 50%
            delay = self.base_delay * random.uniform(0.5, 1.5)
            await asyncio.sleep(delay)

    async def get(self, url, **kwargs) -> Optional[httpx.Response]:
        """
        封装的 GET 请求
        1. 自动延时
        2. 自动重试 (遇到 429/5xx)
        """
        await self._sleep()
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logging.info(f"GET {url} (Attempt {attempt + 1})")
                response = await self.client.get(url, **kwargs)
                
                # 检查状态码
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    wait_time = (attempt + 1) * 5  # 遇到限流，指数级等待 5s, 10s...
                    logging.warning(f"Rate limited (429). Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                elif 500 <= response.status_code < 600:
                    logging.warning(f"Server error ({response.status_code}). Retrying...")
                    await asyncio.sleep(2)
                else:
                    # 其他错误 (404, 403) 直接返回，不重试
                    logging.error(f"Request failed with status {response.status_code}")
                    return response
                    
            except httpx.RequestError as e:
                logging.error(f"Network error: {e}")
                await asyncio.sleep(2)
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                await asyncio.sleep(2)
        
        logging.error("Max retries reached.")
        return None

    async def post(self, url, **kwargs) -> Optional[httpx.Response]:
        """封装的 POST 请求"""
        await self._sleep()
        try:
            return await self.client.post(url, **kwargs)
        except httpx.RequestError as e:
            logging.error(f"Network error in POST: {e}")
            return None

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


