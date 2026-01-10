import requests
from fake_useragent import UserAgent
import time
import random
import logging

# TODO: Migrate to httpx for async support (Phase 1 Requirement)

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
        self.session = requests.Session()
        self.base_delay = base_delay
        self.progress_callback = progress_callback
        
        if use_fake_ua:
            self._rotate_ua()
        else:
            # 默认给一个稳健的 Chrome UA
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
        # 加上通用的浏览器头，减少被识别概率
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def _rotate_ua(self):
        """随机切换 User-Agent"""
        try:
            ua = UserAgent()
            # 这里的 random 只是为了演示，fake_useragent 本身就是随机的
            self.session.headers['User-Agent'] = ua.random
            logging.info(f"User-Agent switched to: {self.session.headers['User-Agent'][:50]}...")
        except Exception as e:
            logging.warning(f"Failed to generate fake UA, using default. Error: {e}")

    def _sleep(self):
        """智能延时：模拟人类操作的随机停顿"""
        if self.base_delay > 0:
            # 随机波动 +/- 50%
            delay = self.base_delay * random.uniform(0.5, 1.5)
            time.sleep(delay)

    def get(self, url, **kwargs):
        """
        封装的 GET 请求
        1. 自动延时
        2. 自动重试 (遇到 429/5xx)
        """
        self._sleep()
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logging.info(f"GET {url} (Attempt {attempt + 1})")
                response = self.session.get(url, **kwargs)
                
                # 检查状态码
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    wait_time = (attempt + 1) * 5  # 遇到限流，指数级等待 5s, 10s...
                    logging.warning(f"Rate limited (429). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif 500 <= response.status_code < 600:
                    logging.warning(f"Server error ({response.status_code}). Retrying...")
                    time.sleep(2)
                else:
                    # 其他错误 (404, 403) 直接返回，不重试
                    logging.error(f"Request failed with status {response.status_code}")
                    return response
                    
            except requests.RequestException as e:
                logging.error(f"Network error: {e}")
                time.sleep(2)
        
        logging.error("Max retries reached.")
        return None

    def post(self, url, **kwargs):
        """封装的 POST 请求"""
        self._sleep()
        return self.session.post(url, **kwargs)

