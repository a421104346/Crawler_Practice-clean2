"""
爬虫包：所有具体爬虫的实现
"""
from backend.crawlers.yahoo import YahooCrawler
from backend.crawlers.movies import MoviesCrawler
from backend.crawlers.jobs import JobsCrawler

__all__ = [
    "YahooCrawler",
    "MoviesCrawler",
    "JobsCrawler"
]
