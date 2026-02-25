"""
API router package
"""
from backend.routers import crawlers, tasks, websocket, auth, monitoring, admin, firecrawl

__all__ = ["crawlers", "tasks", "websocket", "auth", "monitoring", "admin", "firecrawl"]
