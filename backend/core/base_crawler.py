import httpx
from fake_useragent import UserAgent
import asyncio
import random
import logging
from typing import Optional, Any

# Configure logging to monitor crawler activity
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

class BaseCrawler:
    def __init__(self, use_fake_ua=True, base_delay=1.0, progress_callback=None):
        """
        Initialize base crawler
        :param use_fake_ua: Whether to automatically use random User-Agent
        :param base_delay: Base delay per request (seconds), actual delay will fluctuate between 0.5x ~ 1.5x
        :param progress_callback: Progress callback function fn(progress: int, message: str)
        """
        self.base_delay = base_delay
        self.progress_callback = progress_callback
        self.use_fake_ua = use_fake_ua
        
        # Initialize headers
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if use_fake_ua:
            self._rotate_ua()
        else:
            # Default to a stable Chrome UA
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            
        # Create async client
        self.client = httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=30.0)

    def _rotate_ua(self):
        """Randomly rotate User-Agent"""
        try:
            ua = UserAgent()
            self.headers['User-Agent'] = ua.random
            logging.info(f"User-Agent switched to: {self.headers['User-Agent'][:50]}...")
            # If client already exists, update headers
            if hasattr(self, 'client'):
                self.client.headers.update({'User-Agent': self.headers['User-Agent']})
        except Exception as e:
            logging.warning(f"Failed to generate fake UA, using default. Error: {e}")

    async def _sleep(self):
        """Smart delay: random pause to simulate human behavior"""
        if self.base_delay > 0:
            # Random fluctuation +/- 50%
            delay = self.base_delay * random.uniform(0.5, 1.5)
            await asyncio.sleep(delay)

    async def get(self, url, **kwargs) -> Optional[httpx.Response]:
        """
        Wrapped GET request
        1. Auto delay
        2. Auto retry (on 429/5xx)
        """
        await self._sleep()
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logging.info(f"GET {url} (Attempt {attempt + 1})")
                response = await self.client.get(url, **kwargs)
                
                # Check status code
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    wait_time = (attempt + 1) * 5  # Rate limited, exponential wait 5s, 10s...
                    logging.warning(f"Rate limited (429). Waiting {wait_time}s...")
                    if self.use_fake_ua:
                        self._rotate_ua()  # Switch UA and retry
                    await asyncio.sleep(wait_time)
                elif response.status_code == 403:
                    # 403 Forbidden may mean UA is blocked
                    logging.warning(f"Access Forbidden (403). Changing UA and retrying...")
                    if self.use_fake_ua:
                        self._rotate_ua()
                    await asyncio.sleep(2)
                elif 500 <= response.status_code < 600:
                    logging.warning(f"Server error ({response.status_code}). Retrying...")
                    await asyncio.sleep(2)
                else:
                    # Other errors (404, 403) return directly, no retry
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
        """Wrapped POST request"""
        await self._sleep()
        try:
            return await self.client.post(url, **kwargs)
        except httpx.RequestError as e:
            logging.error(f"Network error in POST: {e}")
            return None

    async def close(self):
        """Close client"""
        await self.client.aclose()


