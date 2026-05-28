from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BackgroundJobData(BaseModel):
    id: UUID
    institution_id: UUID
    actor_user_id: UUID | None
    job_type: str
    queue_name: str
    status: str
    progress: int
    retry_count: int
    max_retries: int
    idempotency_key: str | None
    celery_task_id: str | None
    input_payload: dict | None
    result_payload: dict | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    failed_at: datetime | None
    cancelled_at: datetime | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobEventData(BaseModel):
    id: UUID
    institution_id: UUID
    job_id: UUID
    event_type: str
    message: str | None
    payload: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobDetailData(BaseModel):
    job: BackgroundJobData
    events: list[JobEventData]


class JobCancelRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)
