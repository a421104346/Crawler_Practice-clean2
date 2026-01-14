"""
爬虫服务：管理所有爬虫的注册和执行
"""
import sys
import os
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
import json

# 添加项目根目录到路径
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
    """爬虫服务类：统一管理所有爬虫"""
    
    def __init__(self):
        # 爬虫注册表：name -> (class, info)
        self._crawlers: Dict[str, tuple[type, CrawlerInfo]] = {}
        self._register_default_crawlers()
    
    def _register_default_crawlers(self):
        """注册默认的爬虫"""
        # Yahoo Finance 爬虫
        self.register_crawler(
            name="yahoo",
            crawler_class=YahooCrawler,
            info=CrawlerInfo(
                name="yahoo",
                display_name="Yahoo Finance",
                description="抓取 Yahoo Finance 股票数据（价格、市值等）",
                parameters=["symbol"],
                optional_parameters=[],
                status="active"
            )
        )
        
        # 豆瓣电影爬虫
        self.register_crawler(
            name="movies",
            crawler_class=MoviesCrawler,
            info=CrawlerInfo(
                name="movies",
                display_name="豆瓣电影 Top250",
                description="抓取豆瓣电影 Top250 榜单（电影名、评分、年份等）",
                parameters=[],
                optional_parameters=["max_pages"],
                status="active"
            )
        )
        
        # Remotive 招聘爬虫
        self.register_crawler(
            name="jobs",
            crawler_class=JobsCrawler,
            info=CrawlerInfo(
                name="jobs",
                display_name="Remotive 远程招聘",
                description="抓取 Remotive 远程工作招聘信息（岗位、公司、薪资等）",
                parameters=[],
                optional_parameters=["category", "search"],
                status="active"
            )
        )

        # 微博热搜爬虫
        self.register_crawler(
            name="weibo",
            crawler_class=WeiboCrawler,
            info=CrawlerInfo(
                name="weibo",
                display_name="微博热搜",
                description="抓取微博实时热搜榜 (使用 Playwright)",
                parameters=[],
                optional_parameters=[],
                status="active"
            )
        )

        # 小红书爬虫
        self.register_crawler(
            name="rednote",
            crawler_class=RednoteCrawler,
            info=CrawlerInfo(
                name="rednote",
                display_name="小红书发现页",
                description="抓取小红书发现页推荐内容 (使用 Playwright)",
                parameters=[],
                optional_parameters=[],
                status="active"
            )
        )

        # ProSettings 爬虫
        self.register_crawler(
            name="prosettings",
            crawler_class=ProSettingsCrawler,
            info=CrawlerInfo(
                name="prosettings",
                display_name="CS2 职业哥设置",
                description="抓取 CS2 职业选手的鼠标设置 (使用 lxml)",
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
        注册新爬虫
        
        Args:
            name: 爬虫唯一标识
            crawler_class: 爬虫类（必须继承 BaseCrawler）
            info: 爬虫信息
        """
        if not issubclass(crawler_class, BaseCrawler):
            raise ValueError(f"Crawler class must inherit from BaseCrawler")
        
        self._crawlers[name] = (crawler_class, info)
        logger.info(f"Registered crawler: {name}")
    
    def get_crawler_info(self, name: str) -> Optional[CrawlerInfo]:
        """获取爬虫信息"""
        if name not in self._crawlers:
            return None
        return self._crawlers[name][1]
    
    def list_crawlers(self) -> list[CrawlerInfo]:
        """列出所有可用的爬虫"""
        return [info for _, info in self._crawlers.values()]
    
    def get_crawler_instance(
        self, 
        crawler_type: str, 
        params: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> BaseCrawler:
        """
        创建爬虫实例
        
        Args:
            crawler_type: 爬虫类型
            params: 初始化参数（可选）
            progress_callback: 进度回调函数
        
        Returns:
            爬虫实例
        
        Raises:
            ValueError: 如果爬虫类型不存在
        """
        if crawler_type not in self._crawlers:
            available = ", ".join(self._crawlers.keys())
            raise ValueError(
                f"Unknown crawler type: {crawler_type}. "
                f"Available crawlers: {available}"
            )
        
        crawler_class = self._crawlers[crawler_type][0]
        params = params or {}
        
        # 实例化爬虫
        crawler = None
        
        # 根据不同爬虫类型，使用不同的初始化参数
        if crawler_type == "yahoo":
            # YahooCrawler 不需要初始化参数
            crawler = crawler_class()
        elif crawler_type == "movies":
            # MoviesCrawler 接受 max_pages 参数
            max_pages = params.get("max_pages", 1)
            # 确保类型转换
            if isinstance(max_pages, str):
                try:
                    max_pages = int(max_pages)
                except ValueError:
                    max_pages = 1
            crawler = crawler_class(max_pages=max_pages)
        elif crawler_type == "jobs":
            # JobsCrawler 接受 category 和 search 参数
            category = params.get("category")
            search = params.get("search")
            crawler = crawler_class(category=category, search=search)
        elif crawler_type in ["weibo", "rednote", "prosettings"]:
            # 这些爬虫暂时不需要初始化参数
            crawler = crawler_class()
        else:
            # 默认：尝试无参数初始化
            crawler = crawler_class()
            
        # 注入进度回调
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
        异步执行爬虫
        
        Args:
            crawler_type: 爬虫类型
            params: 爬虫参数
            progress_callback: 异步进度回调函数 async fn(progress: int, message: str)
        
        Returns:
            爬虫执行结果
        """
        try:
            # 创建爬虫实例
            # 注意：这里直接传入 async 的 progress_callback，因为 BaseCrawler 的子类现在都支持 async
            crawler = self.get_crawler_instance(crawler_type, params, progress_callback=progress_callback)
            
            logger.info(f"Starting crawler: {crawler_type} with params: {params}")
            
            # 根据不同爬虫类型调用不同的方法
            if crawler_type == "yahoo":
                symbol = params.get("symbol")
                if not symbol:
                    raise ValueError("Yahoo crawler requires 'symbol' parameter")
                
                if progress_callback:
                    await progress_callback(10, f"正在初始化 Yahoo 爬虫...")
                
                if progress_callback:
                    await progress_callback(30, f"正在获取 {symbol} 的数据...")
                
                # 直接异步调用
                result = await crawler.get_quote(symbol)
                
                if progress_callback:
                    await progress_callback(90, "数据处理中...")
                
                if not result:
                    raise ValueError(f"No data found for symbol: {symbol}")
                
                if progress_callback:
                    await progress_callback(100, "完成！")
                
                return result
            
            # 对于其他所有遵循标准 run() 接口的爬虫
            elif crawler_type in ["movies", "jobs", "weibo", "rednote", "prosettings"]:
                if progress_callback:
                    await progress_callback(5, f"正在初始化 {crawler_type} 爬虫...")
                
                # 直接异步调用
                result = await crawler.run(progress_callback=progress_callback)
                
                return result
            
            else:
                raise NotImplementedError(f"Crawler {crawler_type} not implemented yet")
                
        except Exception as e:
            logger.error(f"Error running crawler {crawler_type}: {e}", exc_info=True)
            raise

# 创建全局服务实例
crawler_service = CrawlerService()
