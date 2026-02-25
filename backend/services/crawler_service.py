"""
Crawler service: manages registration and execution of all crawlers
"""
import sys
import os
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
import json
import inspect

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.base_crawler import BaseCrawler
from backend.crawlers.yahoo import YahooCrawler
from backend.crawlers.movies import MoviesCrawler
from backend.crawlers.jobs import JobsCrawler
from backend.crawlers.weibo import WeiboCrawler
from backend.crawlers.rednote import RednoteCrawler
from backend.crawlers.prosettings import ProSettingsCrawler
from backend.schemas.crawler import CrawlerInfo

logger = logging.getLogger(__name__)


class CrawlerService:
    """Crawler service class: unified management of all crawlers"""
    
    def __init__(self):
        # Crawler registry: name -> (class, info)
        self._crawlers: Dict[str, tuple[type, CrawlerInfo]] = {}
        self._register_default_crawlers()
    
    def _register_default_crawlers(self):
        """Register default crawlers"""
        # Yahoo Finance crawler
        self.register_crawler(
            name="yahoo",
            crawler_class=YahooCrawler,
            info=CrawlerInfo(
                name="yahoo",
                display_name="Yahoo Finance",
                description="Scrape Yahoo Finance stock data (price, market cap, etc.)",
                parameters=["symbol"],
                optional_parameters=[],
                status="active"
            )
        )
        
        # Douban Movies crawler
        self.register_crawler(
            name="movies",
            crawler_class=MoviesCrawler,
            info=CrawlerInfo(
                name="movies",
                display_name="Douban Movies Top250",
                description="Scrape Douban Movies Top250 list (title, rating, year, etc.)",
                parameters=[],
                optional_parameters=["max_pages"],
                status="active"
            )
        )
        
        # Remotive Jobs crawler
        self.register_crawler(
            name="jobs",
            crawler_class=JobsCrawler,
            info=CrawlerInfo(
                name="jobs",
                display_name="Remotive Remote Jobs",
                description="Scrape Remotive remote job listings (position, company, salary, etc.)",
                parameters=[],
                optional_parameters=["category", "search"],
                status="active"
            )
        )

        # Weibo Hot Search crawler
        self.register_crawler(
            name="weibo",
            crawler_class=WeiboCrawler,
            info=CrawlerInfo(
                name="weibo",
                display_name="Weibo Hot Search",
                description="Scrape Weibo real-time hot search list (using Playwright)",
                parameters=[],
                optional_parameters=[],
                status="active"
            )
        )

        # Xiaohongshu crawler
        self.register_crawler(
            name="rednote",
            crawler_class=RednoteCrawler,
            info=CrawlerInfo(
                name="rednote",
                display_name="Xiaohongshu Explore",
                description="Scrape Xiaohongshu explore page recommendations (using Playwright)",
                parameters=[],
                optional_parameters=[],
                status="active"
            )
        )

        # ProSettings crawler
        self.register_crawler(
            name="prosettings",
            crawler_class=ProSettingsCrawler,
            info=CrawlerInfo(
                name="prosettings",
                display_name="CS2 Pro Player Settings",
                description="Scrape CS2 pro player mouse settings (using lxml)",
                parameters=[],
                optional_parameters=[],
                status="active"
            )
        )
    
    def register_crawler(
        self,
        name: str,
        crawler_class: type,
        info: CrawlerInfo
    ):
        """
        Register new crawler
        
        Args:
            name: Unique crawler identifier
            crawler_class: Crawler class (must extend BaseCrawler)
            info: Crawler info
        """
        if not issubclass(crawler_class, BaseCrawler):
            raise ValueError(f"Crawler class must inherit from BaseCrawler")
        
        self._crawlers[name] = (crawler_class, info)
        logger.info(f"Registered crawler: {name}")
    
    def get_crawler_info(self, name: str) -> Optional[CrawlerInfo]:
        """Get crawler info"""
        if name not in self._crawlers:
            return None
        return self._crawlers[name][1]
    
    def list_crawlers(self) -> list[CrawlerInfo]:
        """List all available crawlers"""
        return [info for _, info in self._crawlers.values()]
    
    def get_crawler_instance(
        self, 
        crawler_type: str, 
        params: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> BaseCrawler:
        """
        Create crawler instance
        
        Args:
            crawler_type: Crawler type
            params: Initialization parameters (optional)
            progress_callback: Progress callback function
        
        Returns:
            Crawler instance
        
        Raises:
            ValueError: If crawler type does not exist
        """
        if crawler_type not in self._crawlers:
            available = ", ".join(self._crawlers.keys())
            raise ValueError(
                f"Unknown crawler type: {crawler_type}. "
                f"Available crawlers: {available}"
            )
        
        crawler_class = self._crawlers[crawler_type][0]
        params = params or {}
        
        # Instantiate crawler
        crawler = None
        
        # Use different initialization parameters based on crawler type
        if crawler_type == "yahoo":
            # YahooCrawler doesn't need initialization parameters
            crawler = crawler_class()
        elif crawler_type == "movies":
            # MoviesCrawler accepts max_pages parameter
            max_pages = params.get("max_pages", 1)
            # Ensure type conversion
            if isinstance(max_pages, str):
                try:
                    max_pages = int(max_pages)
                except ValueError:
                    max_pages = 1
            crawler = crawler_class(max_pages=max_pages)
        elif crawler_type == "jobs":
            # JobsCrawler accepts category and search parameters
            category = params.get("category")
            search = params.get("search")
            crawler = crawler_class(category=category, search=search)
        elif crawler_type in ["weibo", "rednote", "prosettings"]:
            # These crawlers don't need initialization parameters for now
            crawler = crawler_class()
        else:
            # Default: try initialization without parameters
            crawler = crawler_class()
            
        # Inject progress callback
        if progress_callback:
            crawler.progress_callback = progress_callback
            
        return crawler
    
    async def run_crawler(
        self,
        crawler_type: str,
        params: Dict[str, Any],
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Any:
        """
        Execute crawler asynchronously
        
        Args:
            crawler_type: Crawler type
            params: Crawler parameters
            progress_callback: Async progress callback function async fn(progress: int, message: str)
        
        Returns:
            Crawler execution result
        """
        try:
            # Create crawler instance
            # Note: directly passing async progress_callback since BaseCrawler subclasses now support async
            crawler = self.get_crawler_instance(crawler_type, params, progress_callback=progress_callback)
            
            logger.info(f"Starting crawler: {crawler_type} with params: {params}")
            
            # Call different methods based on crawler type
            if crawler_type == "yahoo":
                symbol = params.get("symbol")
                if not symbol:
                    raise ValueError("Yahoo crawler requires 'symbol' parameter")
                
                if progress_callback:
                    await progress_callback(10, f"Initializing Yahoo crawler...")
                
                if progress_callback:
                    await progress_callback(30, f"Fetching data for {symbol}...")
                
                # Direct async call
                result = await crawler.get_quote(symbol)
                
                if progress_callback:
                    await progress_callback(90, "Processing data...")
                
                if not result:
                    raise ValueError(f"No data found for symbol: {symbol}")
                
                if progress_callback:
                    await progress_callback(100, "Done!")
                
                return result
            
            # For all other crawlers following the standard run() interface
            elif crawler_type in ["movies", "jobs", "weibo", "rednote", "prosettings"]:
                if progress_callback:
                    await progress_callback(5, f"Initializing {crawler_type} crawler...")
                
                # Direct async call (compatible with run() that doesn't support progress_callback)
                run_method = crawler.run
                supports_progress = False
                for param in inspect.signature(run_method).parameters.values():
                    if param.name == "progress_callback" or param.kind == inspect.Parameter.VAR_KEYWORD:
                        supports_progress = True
                        break

                if progress_callback and supports_progress:
                    result = await run_method(progress_callback=progress_callback)
                else:
                    result = await run_method()
                
                return result
            
            else:
                raise NotImplementedError(f"Crawler {crawler_type} not implemented yet")
                
        except Exception as e:
            logger.error(f"Error running crawler {crawler_type}: {e}", exc_info=True)
            raise

# Create global service instance
crawler_service = CrawlerService()
