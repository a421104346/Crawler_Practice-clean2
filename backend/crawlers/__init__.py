"""
Crawlers package: all concrete crawler implementations
"""
from backend.crawlers.yahoo import YahooCrawler
from backend.crawlers.movies import MoviesCrawler
from backend.crawlers.jobs import JobsCrawler

__all__ = [
    "YahooCrawler",
    "MoviesCrawler",
    "JobsCrawler"
]
