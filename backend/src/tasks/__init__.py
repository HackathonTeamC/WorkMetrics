from celery import Celery
from celery.schedules import crontab

from src.config.settings import settings

# Create Celery app
celery_app = Celery(
    "workmetrics",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.tasks.daily_refresh"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000,  # 50 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "daily-metrics-refresh": {
        "task": "src.tasks.daily_refresh.refresh_all_projects",
        "schedule": crontab(
            hour=settings.daily_batch_hour, minute=settings.daily_batch_minute
        ),
    },
}

__all__ = ["celery_app"]
