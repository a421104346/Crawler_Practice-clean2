"""
Pydantic 模型包：用于API请求/响应验证
"""
from backend.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskListResponse,
    TaskUpdate
)
from backend.schemas.crawler import (
    CrawlerRequest,
    CrawlerResponse,
    CrawlerInfo
)
from backend.schemas.firecrawl import (
    FirecrawlScrapeRequest,
    FirecrawlScrapeResponse,
    FirecrawlWeiboHotRankRequest,
    FirecrawlWeiboHotRankResponse,
    FirecrawlWeiboHotRankResult,
    WeiboHotRankPost
)

__all__ = [
    "TaskCreate",
    "TaskResponse",
    "TaskListResponse",
    "TaskUpdate",
    "CrawlerRequest",
    "CrawlerResponse",
    "CrawlerInfo",
    "FirecrawlScrapeRequest",
    "FirecrawlScrapeResponse",
    "FirecrawlWeiboHotRankRequest",
    "FirecrawlWeiboHotRankResponse",
    "FirecrawlWeiboHotRankResult",
    "WeiboHotRankPost"
]
