"""
爬虫包：所有具体爬虫的实现
"""
from crawlers.yahoo import YahooCrawler
from crawlers.movies import MoviesCrawler
from crawlers.jobs import JobsCrawler

__all__ = [
    "YahooCrawler",
    "MoviesCrawler",
    "JobsCrawler"
]
