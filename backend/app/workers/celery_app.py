"""
Celery Worker Configuration
Connects to Redis message broker for scalable asynchronous background processing.
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "knowledge_assistant_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes maximum per file
)
