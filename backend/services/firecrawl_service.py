"""
Firecrawl 服务：封装第三方 API 调用
"""
from typing import Any, Dict
import logging

import httpx

from backend.config import settings
from backend.schemas.firecrawl import FirecrawlScrapeRequest, FirecrawlScrapeResponse

__all__ = ["scrape_firecrawl"]

logger = logging.getLogger(__name__)


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
