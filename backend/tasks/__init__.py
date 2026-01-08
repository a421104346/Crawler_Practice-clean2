"""
Celery 任务包
"""
from backend.tasks.crawler_tasks import run_crawler_task

__all__ = ["run_crawler_task"]
