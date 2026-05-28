from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from celery.result import AsyncResult
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BackgroundJob, BackgroundJobStatus, JobEvent
from app.repositories.jobs_repository import JobsRepository
from app.workers.celery_app import celery_app

TERMINAL_STATUSES = {
    BackgroundJobStatus.completed,
    BackgroundJobStatus.failed,
    BackgroundJobStatus.cancelled,
}


class JobsService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = JobsRepository(session)

    async def create_and_enqueue(
        self,
        *,
        institution_id: UUID,
        actor_user_id: UUID | None,
        job_type: str,
        queue_name: str,
        task_name: str,
        input_payload: dict | None = None,
        idempotency_key: str | None = None,
        max_retries: int = 3,
    ) -> BackgroundJob:
        if idempotency_key:
            existing = await self.repo.find_by_idempotency_key(institution_id, idempotency_key)
            if existing:
                return existing

        job = BackgroundJob(
            institution_id=institution_id,
            actor_user_id=actor_user_id,
            job_type=job_type,
            queue_name=queue_name,
            input_payload=input_payload,
            idempotency_key=idempotency_key,
            max_retries=max_retries,
        )
        self.repo.add(job)
        await self.repo.flush()
        self._event(job, "queued", "Job queued.", {"task_name": task_name})
        async_result = celery_app.send_task(task_name, args=[str(job.id)], queue=queue_name, routing_key=queue_name)
        job.celery_task_id = async_result.id
        await self.repo.commit()
        return job

    async def get_detail(self, institution_id: UUID, job_id: UUID) -> tuple[BackgroundJob, list[JobEvent]]:
        job = await self.repo.get_job(institution_id, job_id)
        if not job:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
        return job, list(await self.repo.list_events(institution_id, job_id))

    async def cancel_job(
        self,
        institution_id: UUID,
        job_id: UUID,
        *,
        reason: str | None,
    ) -> BackgroundJob:
        job = await self.repo.get_job(institution_id, job_id)
        if not job:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
        if job.status in TERMINAL_STATUSES:
            return job

        if job.celery_task_id:
            AsyncResult(job.celery_task_id, app=celery_app).revoke(terminate=False)

        now = _utc_now()
        job.status = BackgroundJobStatus.cancelled
        job.cancelled_at = now
        job.completed_at = now
        self._event(job, "cancelled", reason or "Job cancelled.", None)
        await self.repo.commit()
        return job

    async def mark_running(self, job_id: UUID) -> BackgroundJob:
        job = await self._get_worker_job(job_id)
        job.status = BackgroundJobStatus.running
        job.started_at = job.started_at or _utc_now()
        self._event(job, "running", "Job started.", None)
        await self.repo.commit()
        return job

    async def update_progress(self, job_id: UUID, progress: int, message: str | None = None) -> BackgroundJob:
        job = await self._get_worker_job(job_id)
        job.progress = max(0, min(progress, 100))
        self._event(job, "progress", message, {"progress": job.progress})
        await self.repo.commit()
        return job

    async def mark_completed(self, job_id: UUID, result_payload: dict | None = None) -> BackgroundJob:
        job = await self._get_worker_job(job_id)
        job.status = BackgroundJobStatus.completed
        job.progress = 100
        job.result_payload = result_payload
        job.completed_at = _utc_now()
        self._event(job, "completed", "Job completed.", result_payload)
        await self.repo.commit()
        return job

    async def mark_failed(self, job_id: UUID, error_message: str, payload: dict | None = None) -> BackgroundJob:
        job = await self._get_worker_job(job_id)
        job.status = BackgroundJobStatus.failed
        job.error_message = error_message
        job.failed_at = _utc_now()
        self._event(job, "failed", error_message, payload)
        await self.repo.commit()
        return job

    async def mark_retrying(self, job_id: UUID, error_message: str) -> BackgroundJob:
        job = await self._get_worker_job(job_id)
        job.status = BackgroundJobStatus.retrying
        job.retry_count += 1
        job.error_message = error_message
        self._event(job, "retrying", error_message, {"retry_count": job.retry_count})
        await self.repo.commit()
        return job

    async def _get_worker_job(self, job_id: UUID) -> BackgroundJob:
        job = await self.repo.get_job_any_tenant(job_id)
        if not job:
            raise RuntimeError(f"Background job {job_id} was not found")
        if job.status == BackgroundJobStatus.cancelled:
            raise RuntimeError(f"Background job {job_id} is cancelled")
        return job

    def _event(self, job: BackgroundJob, event_type: str, message: str | None, payload: dict | None) -> None:
        self.repo.add(
            JobEvent(
                institution_id=job.institution_id,
                job_id=job.id,
                event_type=event_type,
                message=message,
                payload=payload,
            )
        )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
