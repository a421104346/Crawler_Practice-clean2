"""
Firecrawl 测试接口
"""
import logging
from fastapi import APIRouter, Depends, HTTPException

from backend.schemas.auth import TokenData
from backend.schemas.firecrawl import (
    FirecrawlScrapeRequest,
    FirecrawlScrapeResponse,
    FirecrawlWeiboHotRankRequest,
    FirecrawlWeiboHotRankResponse
)
from backend.dependencies import get_current_user
from backend.services.firecrawl_service import scrape_firecrawl, scrape_weibo_hot_rank1_posts

__all__ = ["router"]

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/firecrawl", tags=["firecrawl"])


@router.post("/scrape", response_model=FirecrawlScrapeResponse)
async def scrape(request: FirecrawlScrapeRequest, current_user: TokenData = Depends(get_current_user)):
    """
    使用 Firecrawl 抓取单个页面内容。
    """
    try:
        _ = current_user
        return await scrape_firecrawl(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error in Firecrawl scrape: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Firecrawl scrape failed") from exc


@router.post("/weibo/hot-rank1", response_model=FirecrawlWeiboHotRankResponse)
async def scrape_weibo_hot_rank1(
    request: FirecrawlWeiboHotRankRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    抓取微博热搜 Rank1 话题前五页帖子内容。
    """
    try:
        _ = current_user
        return await scrape_weibo_hot_rank1_posts(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error in Firecrawl hot rank1: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Firecrawl hot rank1 failed") from exc
