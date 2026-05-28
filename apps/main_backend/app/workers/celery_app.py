from celery import Celery
from kombu import Exchange, Queue

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "neurafix_school_os",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.health", "app.tasks.job_tasks", "app.tasks.rag_tasks"],
)

default_exchange = Exchange("neurafix", type="direct")

celery_app.conf.update(
    task_default_queue="default",
    task_default_exchange="neurafix",
    task_default_routing_key="default",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_time_limit=900,
    task_soft_time_limit=840,
    result_expires=86400,
    task_queues=(
        Queue("high_priority", default_exchange, routing_key="high_priority"),
        Queue("default", default_exchange, routing_key="default"),
        Queue("ai_tasks", default_exchange, routing_key="ai_tasks"),
        Queue("rag_ingestion", default_exchange, routing_key="rag_ingestion"),
        Queue("embedding_tasks", default_exchange, routing_key="embedding_tasks"),
        Queue("ocr_tasks", default_exchange, routing_key="ocr_tasks"),
        Queue("pdf_tasks", default_exchange, routing_key="pdf_tasks"),
        Queue("answer_checking", default_exchange, routing_key="answer_checking"),
        Queue("email_queue", default_exchange, routing_key="email_queue"),
        Queue("notification_queue", default_exchange, routing_key="notification_queue"),
        Queue("analytics_queue", default_exchange, routing_key="analytics_queue"),
        Queue("report_queue", default_exchange, routing_key="report_queue"),
        Queue("low_priority", default_exchange, routing_key="low_priority"),
    ),
)
