"""
Firecrawl API request/response models
"""
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field, HttpUrl

__all__ = [
    "FirecrawlScrapeRequest",
    "FirecrawlScrapeResponse",
    "FirecrawlWeiboHotRankRequest",
    "WeiboHotRankPost",
    "FirecrawlWeiboHotRankResult",
    "FirecrawlWeiboHotRankResponse",
]


class FirecrawlScrapeRequest(BaseModel):
    """Firecrawl scrape request"""

    url: HttpUrl = Field(..., description="URL of the page to scrape")
    formats: list[str] = Field(
        default_factory=lambda: ["markdown"],
        min_length=1,
        description="Response format list, e.g. markdown/html/rawHtml/screenshot/json"
    )
    only_main_content: bool = Field(
        default=True,
        description="Whether to return main content only (denoised)"
    )
    wait_for: Optional[int] = Field(
        default=None,
        ge=0,
        description="Page load wait time in ms (optional)"
    )
    timeout_ms: Optional[int] = Field(
        default=None,
        ge=1000,
        description="Request timeout in ms (optional)"
    )
    cookie: Optional[str] = Field(
        default=None,
        description="Session cookie (optional, for authenticated pages)"
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Custom request headers (optional)"
    )


class FirecrawlScrapeResponse(BaseModel):
    """Firecrawl scrape response"""

    success: bool = Field(..., description="Whether successful")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message")


class FirecrawlWeiboHotRankRequest(BaseModel):
    """Weibo Hot Search Rank1 scrape request"""

    pages: int = Field(default=5, ge=1, le=5, description="Number of pages to scrape (default: first 5)")
    wait_for: Optional[int] = Field(
        default=None,
        ge=0,
        description="Page load wait time in ms (optional)"
    )
    timeout_ms: Optional[int] = Field(
        default=None,
        ge=1000,
        description="Request timeout in ms (optional)"
    )
    cookie: Optional[str] = Field(
        default=None,
        description="Session cookie (optional, for authenticated pages)"
    )


class WeiboHotRankPost(BaseModel):
    """Post under Weibo hot search topic"""

    username: str = Field(..., description="Username")
    user_link: str = Field(..., description="User profile link")
    content: str = Field(..., description="Post content")


class FirecrawlWeiboHotRankResult(BaseModel):
    """Weibo Hot Search Rank1 scrape result"""

    topic_title: str = Field(..., description="Hot search topic title")
    topic_url: str = Field(..., description="Hot search topic URL")
    pages: int = Field(..., description="Actual pages scraped")
    total_posts: int = Field(..., description="Total posts")
    posts: List[WeiboHotRankPost] = Field(default_factory=list, description="Post list")


class FirecrawlWeiboHotRankResponse(BaseModel):
    """Weibo Hot Search Rank1 scrape response"""

    success: bool = Field(..., description="Whether successful")
    data: Optional[FirecrawlWeiboHotRankResult] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message")
