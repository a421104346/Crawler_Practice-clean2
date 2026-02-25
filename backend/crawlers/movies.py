"""
Douban Movies Top250 crawler
"""
from backend.core.base_crawler import BaseCrawler
import re
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class MoviesCrawler(BaseCrawler):
    """Douban Movies Top250 crawler"""
    
    def __init__(self, max_pages: int = 1, progress_callback=None):
        """
        Initialize movies crawler
        
        Args:
            max_pages: Number of pages to crawl (25 movies per page, 10 pages=250)
            progress_callback: Progress callback function
        """
        super().__init__(use_fake_ua=True, base_delay=2.0, progress_callback=progress_callback)
        self.max_pages = max_pages
        self.base_url = "https://movie.douban.com/top250"
        
        # Set specific headers
        self.client.headers.update({
            'Referer': 'https://movie.douban.com/'
        })
        
        self.movies = []
    
    async def fetch_page(self, start: int) -> str:
        """
        Fetch a single page
        
        Args:
            start: Start index (0, 25, 50...)
        
        Returns:
            HTML content
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
        Parse HTML to extract movie info
        
        Args:
            html: Page HTML
        
        Returns:
            Movie list
        """
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("div", class_="item")
        
        page_movies = []
        
        for item in items:
            try:
                # 1. Title
                title = item.find("span", class_="title").get_text()
                
                # 2. Rating
                rating = item.find("span", class_="rating_num").get_text()
                
                # 3. Number of reviews
                people_span = item.find("span", string=re.compile("人评价"))
                if people_span:
                    people_count = re.sub(r'\D', '', people_span.get_text())
                else:
                    people_count = 0
                
                # 4. Year
                info_text = item.find("div", class_="bd").p.get_text()
                year_match = re.search(r'\d{4}', info_text)
                year = year_match.group() if year_match else "Unknown"
                
                # 5. Director and actor info (optional)
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
    
    async def run(self, progress_callback=None) -> dict:
        """
        Execute crawler workflow
        
        Returns:
            Crawl results: {"movies": [...], "total": N}
        """
        if progress_callback:
            self.progress_callback = progress_callback
        logger.info(f"Starting movies crawler: max_pages={self.max_pages}")
        
        self.movies = []
        
        for i in range(self.max_pages):
            # Update progress
            if self.progress_callback:
                logger.info(f"Calling progress callback for page {i+1}")
                # Progress calculation: assume scraping is 80%, processing is 20%
                # Current page progress = (i / max_pages) * 80
                progress = int((i / self.max_pages) * 80) + 10  # +10 for the initialization phase
                
                # Handle async callback
                import inspect
                if inspect.iscoroutinefunction(self.progress_callback):
                    await self.progress_callback(progress, f"Scraping page {i+1}/{self.max_pages}...")
                else:
                    self.progress_callback(progress, f"Scraping page {i+1}/{self.max_pages}...")
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
                        await self.progress_callback(progress, f"Failed to scrape page {i+1}")
                    else:
                        self.progress_callback(progress, f"Failed to scrape page {i+1}")
                break
        
        # Scraping complete, preparing results
        if self.progress_callback:
            if inspect.iscoroutinefunction(self.progress_callback):
                await self.progress_callback(90, "Organizing data...")
            else:
                self.progress_callback(90, "Organizing data...")
            
        result = {
            "movies": self.movies,
            "total": len(self.movies),
            "pages_crawled": min(i + 1, self.max_pages)
        }
        
        logger.info(f"Movies crawler completed: {len(self.movies)} movies")
        
        if self.progress_callback:
            if inspect.iscoroutinefunction(self.progress_callback):
                await self.progress_callback(100, "Done!")
            else:
                self.progress_callback(100, "Done!")
            
        return result
