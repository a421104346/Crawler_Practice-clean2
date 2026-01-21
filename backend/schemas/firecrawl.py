"""
Firecrawl 接口的请求/响应模型
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
    """Firecrawl 抓取请求"""

    url: HttpUrl = Field(..., description="需要抓取的页面 URL")
    formats: list[str] = Field(
        default_factory=lambda: ["markdown"],
        min_length=1,
        description="返回格式列表，例如 markdown/html/rawHtml/screenshot/json"
    )
    only_main_content: bool = Field(
        default=True,
        description="是否仅返回主内容（去噪）"
    )
    wait_for: Optional[int] = Field(
        default=None,
        ge=0,
        description="等待页面加载的毫秒数（可选）"
    )
    timeout_ms: Optional[int] = Field(
        default=None,
        ge=1000,
        description="请求超时毫秒数（可选）"
    )
    cookie: Optional[str] = Field(
        default=None,
        description="登录态 Cookie（可选，用于登录后页面）"
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="自定义请求头（可选）"
    )


class FirecrawlScrapeResponse(BaseModel):
    """Firecrawl 抓取响应"""

    success: bool = Field(..., description="是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="返回数据")
    error: Optional[str] = Field(default=None, description="错误信息")


class FirecrawlWeiboHotRankRequest(BaseModel):
    """微博热搜 Rank1 抓取请求"""

    pages: int = Field(default=5, ge=1, le=5, description="抓取页数（默认前 5 页）")
    wait_for: Optional[int] = Field(
        default=None,
        ge=0,
        description="等待页面加载的毫秒数（可选）"
    )
    timeout_ms: Optional[int] = Field(
        default=None,
        ge=1000,
        description="请求超时毫秒数（可选）"
    )
    cookie: Optional[str] = Field(
        default=None,
        description="登录态 Cookie（可选，用于登录后页面）"
    )


class WeiboHotRankPost(BaseModel):
    """微博热搜话题下的帖子"""

    username: str = Field(..., description="用户名")
    user_link: str = Field(..., description="用户主页链接")
    content: str = Field(..., description="帖子内容")


class FirecrawlWeiboHotRankResult(BaseModel):
    """微博热搜 Rank1 抓取结果"""

    topic_title: str = Field(..., description="热搜话题标题")
    topic_url: str = Field(..., description="热搜话题链接")
    pages: int = Field(..., description="实际抓取页数")
    total_posts: int = Field(..., description="帖子总数")
    posts: List[WeiboHotRankPost] = Field(default_factory=list, description="帖子列表")


class FirecrawlWeiboHotRankResponse(BaseModel):
    """微博热搜 Rank1 抓取响应"""

    success: bool = Field(..., description="是否成功")
    data: Optional[FirecrawlWeiboHotRankResult] = Field(default=None, description="返回数据")
    error: Optional[str] = Field(default=None, description="错误信息")
