from __future__ import annotations

import asyncio
from uuid import UUID

from app.db.session import AsyncSessionLocal
from app.services.jobs_service import JobsService
from app.workers.celery_app import celery_app


async def _run_placeholder(job_id: str, task_label: str) -> dict[str, str]:
    parsed_job_id = UUID(job_id)
    async with AsyncSessionLocal() as db:
        service = JobsService(db)
        await service.mark_running(parsed_job_id)
        await service.update_progress(parsed_job_id, 50, f"{task_label} placeholder reached midpoint.")
        await service.mark_completed(parsed_job_id, {"message": f"{task_label} placeholder completed."})
    return {"job_id": job_id, "status": "completed"}


@celery_app.task(name="jobs.placeholder", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def placeholder_task(self, job_id: str, task_label: str = "background job") -> dict[str, str]:
    try:
        return asyncio.run(_run_placeholder(job_id, task_label))
    except Exception as exc:
        parsed_job_id = UUID(job_id)

        async def mark_failure() -> None:
            async with AsyncSessionLocal() as db:
                service = JobsService(db)
                if self.request.retries < 3:
                    await service.mark_retrying(parsed_job_id, str(exc))
                else:
                    await service.mark_failed(parsed_job_id, str(exc))

        asyncio.run(mark_failure())
        raise
