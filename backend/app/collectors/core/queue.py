"""
app/collectors/core/queue.py
────────────────────────────
Celery application configuration for the Event Queue.

Source: Chapter 4, Section 4.4.4
Quote: "extracted records are placed on a message queue that provides
        buffering and automatic retry in the event of a downstream failure"
"""

from celery import Celery
from kombu import Exchange, Queue

from app.core.config import settings

celery_app = Celery(
    "rugpull_collectors",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Route different types of events to specific queues
    task_routes={
        "app.collectors.workers.tasks.process_transaction": {"queue": "transactions"},
        "app.collectors.workers.tasks.process_liquidity_event": {"queue": "liquidity"},
        "app.collectors.workers.tasks.process_contract_metadata": {"queue": "contracts"},
        "app.collectors.workers.tasks.process_token_metadata": {"queue": "tokens"},
        "app.collectors.workers.tasks.backfill_historical_data": {"queue": "backfill"},
    },
    task_queues=(
        Queue("transactions", Exchange("transactions"), routing_key="transactions"),
        Queue("liquidity", Exchange("liquidity"), routing_key="liquidity"),
        Queue("contracts", Exchange("contracts"), routing_key="contracts"),
        Queue("tokens", Exchange("tokens"), routing_key="tokens"),
        Queue("backfill", Exchange("backfill"), routing_key="backfill"),
    ),
    # Acknowledge task only after it has been executed successfully
    task_acks_late=True,
    # Prefetch multiplier to optimize for I/O bound database writes
    worker_prefetch_multiplier=4,
)
