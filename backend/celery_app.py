"""
Celery application configuration: distributed task queue
"""
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery application
celery_app = Celery(
    "crawler_tasks",
    broker=settings.REDIS_URL or "redis://localhost:6379/0",
    backend=settings.REDIS_URL or "redis://localhost:6379/0",
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minute timeout
    task_soft_time_limit=25 * 60,  # 25 minute soft timeout
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)


@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Pre-task hook"""
    logger.info(f"Task {task.name} [{task_id}] started")


@task_postrun.connect
def task_postrun_handler(task_id, task, *args, **kwargs):
    """Post-task hook"""
    logger.info(f"Task {task.name} [{task_id}] completed")


@task_failure.connect
def task_failure_handler(task_id, exception, *args, **kwargs):
    """Task failure hook"""
    logger.error(f"Task [{task_id}] failed: {exception}")


# Import tasks (ensure tasks are registered)
from backend.tasks import crawler_tasks  # noqa
