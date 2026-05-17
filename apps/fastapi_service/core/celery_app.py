from celery import Celery
from core.config import settings

celery_app = Celery(
    "video_processor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["movies.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
)
