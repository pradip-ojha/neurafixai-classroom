from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BackgroundJob, BackgroundJobStatus, JobEvent


class JobsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, entity: object) -> None:
        self.session.add(entity)

    async def flush(self) -> None:
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def get_job(self, institution_id: UUID, job_id: UUID) -> BackgroundJob | None:
        result = await self.session.execute(
            select(BackgroundJob).where(
                BackgroundJob.id == job_id,
                BackgroundJob.institution_id == institution_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_job_any_tenant(self, job_id: UUID) -> BackgroundJob | None:
        return await self.session.get(BackgroundJob, job_id)

    async def find_by_idempotency_key(self, institution_id: UUID, key: str) -> BackgroundJob | None:
        result = await self.session.execute(
            select(BackgroundJob).where(
                BackgroundJob.institution_id == institution_id,
                BackgroundJob.idempotency_key == key,
            )
        )
        return result.scalar_one_or_none()

    async def list_jobs(
        self,
        institution_id: UUID,
        limit: int,
        offset: int,
        status: BackgroundJobStatus | None = None,
    ) -> Sequence[BackgroundJob]:
        conditions = [BackgroundJob.institution_id == institution_id]
        if status is not None:
            conditions.append(BackgroundJob.status == status)
        result = await self.session.execute(
            select(BackgroundJob)
            .where(*conditions)
            .order_by(BackgroundJob.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_events(self, institution_id: UUID, job_id: UUID) -> Sequence[JobEvent]:
        result = await self.session.execute(
            select(JobEvent)
            .where(JobEvent.institution_id == institution_id, JobEvent.job_id == job_id)
            .order_by(JobEvent.created_at)
        )
        return result.scalars().all()
