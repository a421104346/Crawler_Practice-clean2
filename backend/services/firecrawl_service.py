"""
Firecrawl 服务：封装第三方 API 调用
"""
from typing import Any, Dict, List, Tuple
import logging
import os
import asyncio
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx
from lxml import html as lxml_html

from backend.config import settings, PROJECT_ROOT
from backend.schemas.firecrawl import (
    FirecrawlScrapeRequest,
    FirecrawlScrapeResponse,
    FirecrawlWeiboHotRankRequest,
    FirecrawlWeiboHotRankResponse,
    FirecrawlWeiboHotRankResult,
    WeiboHotRankPost
)

__all__ = ["scrape_firecrawl", "scrape_weibo_hot_rank1_posts"]

logger = logging.getLogger(__name__)

WEIBO_HOT_URL = "https://s.weibo.com/top/summary?cate=realtimehot"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "firecrawl", "weibo_hot_rank1")


async def _save_html(filename: str, content: str) -> None:
    if not content:
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    await asyncio.to_thread(_write_text_file, path, content)


def _write_text_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def _build_firecrawl_payload(request: FirecrawlScrapeRequest) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "url": str(request.url),
        "formats": request.formats,
        "onlyMainContent": request.only_main_content,
    }
    if request.wait_for is not None:
        payload["waitFor"] = request.wait_for
    if request.timeout_ms is not None:
        payload["timeout"] = request.timeout_ms
    normalized_headers: Dict[str, str] = {}
    if request.headers:
        for key, value in request.headers.items():
            normalized_headers[str(key).lower()] = str(value)
    if request.cookie:
        cookie_value = request.cookie.strip()
        if cookie_value:
            normalized_headers["cookie"] = cookie_value
    if normalized_headers:
        payload_headers = {
            ("Cookie" if key == "cookie" else key): value
            for key, value in normalized_headers.items()
        }
        payload["headers"] = payload_headers
    return payload


async def scrape_firecrawl(request: FirecrawlScrapeRequest) -> FirecrawlScrapeResponse:
    """
    调用 Firecrawl 的 scrape 接口并返回结果。
    """
    if not settings.FIRECRAWL_API_KEY:
        raise ValueError("FIRECRAWL_API_KEY is not configured")

    payload = _build_firecrawl_payload(request)
    headers = {
        "Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}",
        "Content-Type": "application/json",
    }

    timeout_seconds = (request.timeout_ms / 1000) if request.timeout_ms else 30.0
    timeout = httpx.Timeout(timeout_seconds)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.FIRECRAWL_BASE_URL}/v1/scrape",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return FirecrawlScrapeResponse(
                success=bool(data.get("success", False)),
                data=data.get("data"),
                error=data.get("error"),
            )
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code if exc.response else None
        body_preview = exc.response.text[:500] if exc.response else ""
        logger.error(
            "Firecrawl HTTP error: %s (status=%s, body=%s)",
            exc,
            status,
            body_preview,
            exc_info=True
        )
        raise RuntimeError("Firecrawl request failed") from exc
    except httpx.HTTPError as exc:
        logger.error("Firecrawl request error: %s", exc, exc_info=True)
        raise RuntimeError("Firecrawl request error") from exc


def _normalize_weibo_link(link: str) -> str:
    value = link.strip()
    if not value:
        return ""
    if value.startswith("//"):
        return f"https:{value}"
    if value.startswith("http"):
        return value
    if value.startswith("/u/") or value.startswith("/p/"):
        return f"https://weibo.com{value}"
    if value.startswith("/"):
        return f"https://s.weibo.com{value}"
    return f"https://s.weibo.com/{value}"


def _extract_rank1_topic(tree: lxml_html.HtmlElement) -> Tuple[str, str]:
    rows = tree.xpath("//table//tr")
    for row in rows:
        rank_text = "".join(
            row.xpath(".//td[contains(@class,'td-01') or contains(@class,'ranktop')]//text()")
        ).strip()
        if not rank_text:
            rank_text = "".join(row.xpath(".//td[1]//text()")).strip()
        if rank_text.isdigit() and int(rank_text) == 1:
            link_nodes = row.xpath(".//td[contains(@class,'td-02')]//a[1] | .//a[1]")
            if link_nodes:
                title = "".join(link_nodes[0].xpath(".//text()")).strip()
                href = link_nodes[0].get("href") or ""
                if title and href:
                    return title, _normalize_weibo_link(href)

    fallback_links = tree.xpath("//div[@id='pl_top_realtimehot']//a[1] | //table//a[1]")
    if fallback_links:
        title = "".join(fallback_links[0].xpath(".//text()")).strip()
        href = fallback_links[0].get("href") or ""
        if title and href:
            return title, _normalize_weibo_link(href)

    raise ValueError("Failed to locate rank1 topic link on Weibo hot page")


def _build_topic_page_url(topic_url: str, page: int) -> str:
    if page <= 1:
        return topic_url
    parsed = urlparse(topic_url)
    query = parse_qs(parsed.query)
    query["page"] = [str(page)]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def _extract_weibo_posts(tree: lxml_html.HtmlElement) -> Tuple[List[WeiboHotRankPost], int]:
    posts: List[WeiboHotRankPost] = []
    seen: set[tuple[str, str]] = set()
    cards = tree.xpath("//div[contains(@class,'card-wrap')]")
    for card in cards:
        if card.xpath(".//*[contains(@class,'card-top')]"):
            continue

        username = "".join(card.xpath(".//a[contains(@class,'name')]/text()")).strip()
        user_links = card.xpath(".//a[contains(@class,'name')]/@href")
        if not username:
            username = "".join(card.xpath(".//a[@nick-name]/@nick-name")).strip()
            if not username:
                username = "".join(card.xpath(".//a[contains(@href,'/u/')]/text()")).strip()
            if not user_links:
                user_links = card.xpath(".//a[contains(@href,'/u/')]/@href")

        content_parts = card.xpath(".//p[@node-type='feed_list_content_full']//text()")
        if not content_parts:
            content_parts = card.xpath(".//p[@node-type='feed_list_content']//text()")
        if not content_parts:
            content_parts = card.xpath(".//div[contains(@class,'content')]//p[contains(@class,'txt')]//text()")
        if not content_parts:
            content_parts = card.xpath(".//p[contains(@class,'txt')]//text()")
        content = " ".join(part.strip() for part in content_parts if part.strip()).strip()
        if not content:
            continue

        user_link = _normalize_weibo_link(user_links[0]) if user_links else ""
        display_name = username if username else "未知用户"

        key = (display_name, content)
        if key in seen:
            continue
        seen.add(key)

        posts.append(WeiboHotRankPost(username=display_name, user_link=user_link, content=content))
    return posts, len(cards)


def _detect_weibo_blocked(html_content: str) -> str:
    signals = [
        "访问频次过高",
        "安全验证",
        "验证码",
        "请开启 JavaScript",
        "请开启JavaScript",
        "由于您的访问频次过高",
        "请稍后再试"
    ]
    for signal in signals:
        if signal in html_content:
            return signal
    return ""


async def scrape_weibo_hot_rank1_posts(
    request: FirecrawlWeiboHotRankRequest
) -> FirecrawlWeiboHotRankResponse:
    """
    抓取微博热搜 Rank1 话题并采集前五页帖子内容。
    """
    hot_response = await scrape_firecrawl(
        FirecrawlScrapeRequest(
            url=WEIBO_HOT_URL,
            formats=["html"],
            only_main_content=False,
            wait_for=request.wait_for,
            timeout_ms=request.timeout_ms,
            cookie=request.cookie
        )
    )
    if not hot_response.success or not hot_response.data:
        error_message = hot_response.error or "Failed to fetch Weibo hot list"
        return FirecrawlWeiboHotRankResponse(success=False, error=error_message)

    hot_html = hot_response.data.get("html") or hot_response.data.get("rawHtml") or ""
    if not hot_html:
        return FirecrawlWeiboHotRankResponse(success=False, error="Weibo hot list HTML is empty")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    await _save_html(f"hot_list_{timestamp}.html", hot_html)
    blocked_signal = _detect_weibo_blocked(hot_html)
    if blocked_signal:
        logger.warning("Weibo hot list blocked: %s", blocked_signal)
        return FirecrawlWeiboHotRankResponse(
            success=False,
            error=f"Weibo hot list blocked: {blocked_signal}"
        )

    tree = lxml_html.fromstring(hot_html)
    topic_title, topic_url = _extract_rank1_topic(tree)
    logger.info("Weibo hot rank1 topic detected: %s (%s)", topic_title, topic_url)

    total_posts: List[WeiboHotRankPost] = []
    pages = max(1, min(request.pages, 5))
    scraped_pages = 0
    blocked_pages: List[str] = []
    for page in range(1, pages + 1):
        page_url = _build_topic_page_url(topic_url, page)
        page_response = await scrape_firecrawl(
            FirecrawlScrapeRequest(
                url=page_url,
                formats=["html"],
                only_main_content=False,
                wait_for=request.wait_for,
                timeout_ms=request.timeout_ms,
                cookie=request.cookie
            )
        )
        if not page_response.success or not page_response.data:
            logger.warning("Weibo topic page %s fetch failed: %s", page, page_response.error)
            continue
        page_html = page_response.data.get("html") or page_response.data.get("rawHtml") or ""
        if not page_html:
            logger.warning("Weibo topic page %s HTML empty", page)
            continue
        await _save_html(f"topic_page_{timestamp}_p{page}.html", page_html)
        blocked_signal = _detect_weibo_blocked(page_html)
        if blocked_signal:
            blocked_pages.append(f"page {page}: {blocked_signal}")
            logger.warning("Weibo topic page %s blocked: %s", page, blocked_signal)
            continue
        page_tree = lxml_html.fromstring(page_html)
        page_posts, card_count = _extract_weibo_posts(page_tree)
        scraped_pages += 1
        logger.info(
            "Weibo topic page %s parsed: card_count=%s, posts=%s",
            page,
            card_count,
            len(page_posts)
        )
        total_posts.extend(page_posts)

    result = FirecrawlWeiboHotRankResult(
        topic_title=topic_title,
        topic_url=topic_url,
        pages=scraped_pages,
        total_posts=len(total_posts),
        posts=total_posts
    )
    if not total_posts:
        blocked_hint = f" ({'; '.join(blocked_pages)})" if blocked_pages else ""
        return FirecrawlWeiboHotRankResponse(
            success=False,
            data=result,
            error=f"No posts extracted. Possible anti-bot or selector change{blocked_hint}."
        )
    return FirecrawlWeiboHotRankResponse(success=True, data=result)
