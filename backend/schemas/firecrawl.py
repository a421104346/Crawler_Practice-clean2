"""
Firecrawl 接口的请求/响应模型
"""
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, HttpUrl

__all__ = ["FirecrawlScrapeRequest", "FirecrawlScrapeResponse"]


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


class FirecrawlScrapeResponse(BaseModel):
    """Firecrawl 抓取响应"""

    success: bool = Field(..., description="是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="返回数据")
    error: Optional[str] = Field(default=None, description="错误信息")
