"""
豆瓣电影 Top250 爬虫
"""
from backend.core.base_crawler import BaseCrawler
import re
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class MoviesCrawler(BaseCrawler):
    """豆瓣电影 Top250 爬虫"""
    
    def __init__(self, max_pages: int = 1, progress_callback=None):
        """
        初始化电影爬虫
        
        Args:
            max_pages: 要爬取的页数 (每页25部电影，10页=250部)
            progress_callback: 进度回调函数
        """
        super().__init__(use_fake_ua=False, base_delay=2.0, progress_callback=progress_callback)
        self.max_pages = max_pages
        self.base_url = "https://movie.douban.com/top250"
        
        # 设置特定的 headers
        self.client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://movie.douban.com/'
        })
        
        self.movies = []
    
    async def fetch_page(self, start: int) -> str:
        """
        抓取单个页面
        
        Args:
            start: 起始索引 (0, 25, 50...)
        
        Returns:
            HTML 内容
        """
        url = f"{self.base_url}?start={start}"
        logger.info(f"Fetching: {url}")
        
        response = await self.get(url, timeout=10)
        
        if response and response.status_code == 200:
            return response.text
        else:
            logger.error(f"Failed to fetch page at start={start}")
            return None
    
    def parse_page(self, html: str) -> list[dict]:
        """
        解析 HTML 提取电影信息
        
        Args:
            html: 页面 HTML
        
        Returns:
            电影列表
        """
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("div", class_="item")
        
        page_movies = []
        
        for item in items:
            try:
                # 1. 标题
                title = item.find("span", class_="title").get_text()
                
                # 2. 评分
                rating = item.find("span", class_="rating_num").get_text()
                
                # 3. 评价人数
                people_span = item.find("span", string=re.compile("人评价"))
                if people_span:
                    people_count = re.sub(r'\D', '', people_span.get_text())
                else:
                    people_count = 0
                
                # 4. 年份
                info_text = item.find("div", class_="bd").p.get_text()
                year_match = re.search(r'\d{4}', info_text)
                year = year_match.group() if year_match else "Unknown"
                
                # 5. 导演和演员信息（可选）
                director_match = re.search(r'导演:\s*(.*?)(?:\xa0|主演)', info_text)
                director = director_match.group(1).strip() if director_match else "Unknown"
                
                movie = {
                    "title": title,
                    "rating": float(rating),
                    "people_count": int(people_count) if people_count else 0,
                    "year": int(year) if year != "Unknown" else None,
                    "director": director
                }
                
                page_movies.append(movie)
                
            except Exception as e:
                logger.error(f"Error parsing movie item: {e}")
                continue
        
        return page_movies
    
    async def run(self) -> dict:
        """
        执行爬虫流程
        
        Returns:
            爬取结果：{"movies": [...], "total": N}
        """
        logger.info(f"Starting movies crawler: max_pages={self.max_pages}")
        
        self.movies = []
        
        for i in range(self.max_pages):
            # 更新进度
            if self.progress_callback:
                logger.info(f"Calling progress callback for page {i+1}")
                # 进度计算：假设抓取占 80%，处理占 20%
                # 当前页进度 = (i / max_pages) * 80
                progress = int((i / self.max_pages) * 80) + 10  # +10 是因为还有初始化阶段
                
                # 处理 async 回调
                import inspect
                if inspect.iscoroutinefunction(self.progress_callback):
                    await self.progress_callback(progress, f"正在抓取第 {i+1}/{self.max_pages} 页...")
                else:
                    self.progress_callback(progress, f"正在抓取第 {i+1}/{self.max_pages} 页...")
            else:
                logger.warning("No progress_callback provided!")
            
            start = i * 25
            html = await self.fetch_page(start)
            
            if html:
                page_movies = self.parse_page(html)
                self.movies.extend(page_movies)
                logger.info(f"Page {i+1}/{self.max_pages}: {len(page_movies)} movies")
            else:
                logger.warning(f"Failed to fetch page {i+1}, stopping")
                if self.progress_callback:
                    if inspect.iscoroutinefunction(self.progress_callback):
                        await self.progress_callback(progress, f"抓取第 {i+1} 页失败")
                    else:
                        self.progress_callback(progress, f"抓取第 {i+1} 页失败")
                break
        
        # 完成抓取，准备返回
        if self.progress_callback:
            if inspect.iscoroutinefunction(self.progress_callback):
                await self.progress_callback(90, "数据整理中...")
            else:
                self.progress_callback(90, "数据整理中...")
            
        result = {
            "movies": self.movies,
            "total": len(self.movies),
            "pages_crawled": min(i + 1, self.max_pages)
        }
        
        logger.info(f"Movies crawler completed: {len(self.movies)} movies")
        
        if self.progress_callback:
            if inspect.iscoroutinefunction(self.progress_callback):
                await self.progress_callback(100, "完成！")
            else:
                self.progress_callback(100, "完成！")
            
        return result
