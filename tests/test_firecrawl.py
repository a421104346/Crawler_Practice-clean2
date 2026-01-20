"""
Firecrawl API 测试
"""
import pytest

from backend.schemas.firecrawl import FirecrawlScrapeResponse


def test_firecrawl_requires_auth(client):
    """未认证时应返回 403"""
    response = client.post(
        "/api/firecrawl/scrape",
        json={
            "url": "https://s.weibo.com/top/summary?cate=realtimehot",
            "formats": ["markdown"],
            "only_main_content": True,
        },
    )
    assert response.status_code == 403


def test_firecrawl_scrape_success(client, auth_headers, monkeypatch):
    """认证后可正常调用 Firecrawl scrape"""
    async def fake_scrape(_request):
        return FirecrawlScrapeResponse(
            success=True,
            data={"markdown": "# ok", "metadata": {"statusCode": 200}},
            error=None,
        )

    monkeypatch.setattr("backend.routers.firecrawl.scrape_firecrawl", fake_scrape)

    response = client.post(
        "/api/firecrawl/scrape",
        headers=auth_headers,
        json={
            "url": "https://s.weibo.com/top/summary?cate=realtimehot",
            "formats": ["markdown"],
            "only_main_content": True,
            "wait_for": 1200,
            "timeout_ms": 30000,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["markdown"] == "# ok"
