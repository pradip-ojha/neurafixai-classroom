from __future__ import annotations

import asyncio
from uuid import UUID

from app.db.session import AsyncSessionLocal
from app.services.jobs_service import JobsService
from app.services.knowledge_service import KnowledgeService
from app.workers.celery_app import celery_app


async def _ingest_document(job_id: str) -> dict[str, str]:
    parsed_job_id = UUID(job_id)
    async with AsyncSessionLocal() as db:
        jobs = JobsService(db)
        job = await jobs.mark_running(parsed_job_id)
        document_id = UUID(job.input_payload["knowledge_document_id"])
        await jobs.update_progress(parsed_job_id, 20, "Document ingestion started.")
        await KnowledgeService(db).mark_document_indexed_placeholder(document_id)
        await jobs.update_progress(parsed_job_id, 80, "Document chunks and embeddings indexed.")
        await jobs.mark_completed(parsed_job_id, {"knowledge_document_id": str(document_id)})
    return {"job_id": job_id, "status": "completed"}


@celery_app.task(
    name="rag.ingest_document",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def ingest_document_task(self, job_id: str) -> dict[str, str]:
    try:
        return asyncio.run(_ingest_document(job_id))
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
