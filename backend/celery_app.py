"""
Celery 应用配置：分布式任务队列
"""
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# 创建 Celery 应用
celery_app = Celery(
    "crawler_tasks",
    broker=settings.REDIS_URL or "redis://localhost:6379/0",
    backend=settings.REDIS_URL or "redis://localhost:6379/0",
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 分钟超时
    task_soft_time_limit=25 * 60,  # 25 分钟软超时
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)


@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """任务开始前的钩子"""
    logger.info(f"Task {task.name} [{task_id}] started")


@task_postrun.connect
def task_postrun_handler(task_id, task, *args, **kwargs):
    """任务完成后的钩子"""
    logger.info(f"Task {task.name} [{task_id}] completed")


@task_failure.connect
def task_failure_handler(task_id, exception, *args, **kwargs):
    """任务失败的钩子"""
    logger.error(f"Task [{task_id}] failed: {exception}")


# 导入任务（确保任务被注册）
from backend.tasks import crawler_tasks  # noqa
