from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LearningObjective, SyllabusChapter, SyllabusSubtopic, SyllabusTopic


class SyllabusRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, entity: object) -> None:
        self.session.add(entity)

    async def commit(self) -> None:
        await self.session.commit()

    async def get_chapter(self, institution_id: UUID, chapter_id: UUID) -> SyllabusChapter | None:
        return await self._get_tenant_entity(SyllabusChapter, institution_id, chapter_id)

    async def get_topic(self, institution_id: UUID, topic_id: UUID) -> SyllabusTopic | None:
        return await self._get_tenant_entity(SyllabusTopic, institution_id, topic_id)

    async def get_subtopic(self, institution_id: UUID, subtopic_id: UUID) -> SyllabusSubtopic | None:
        return await self._get_tenant_entity(SyllabusSubtopic, institution_id, subtopic_id)

    async def list_chapters(self, institution_id: UUID, limit: int, offset: int) -> Sequence[SyllabusChapter]:
        return await self._list_tenant_entities(SyllabusChapter, institution_id, limit, offset)

    async def list_topics(self, institution_id: UUID, limit: int, offset: int) -> Sequence[SyllabusTopic]:
        return await self._list_tenant_entities(SyllabusTopic, institution_id, limit, offset)

    async def list_subtopics(self, institution_id: UUID, limit: int, offset: int) -> Sequence[SyllabusSubtopic]:
        return await self._list_tenant_entities(SyllabusSubtopic, institution_id, limit, offset)

    async def list_objectives(self, institution_id: UUID, limit: int, offset: int) -> Sequence[LearningObjective]:
        return await self._list_tenant_entities(LearningObjective, institution_id, limit, offset)

    async def _get_tenant_entity(self, model, institution_id: UUID, entity_id: UUID):
        result = await self.session.execute(
            select(model).where(
                model.id == entity_id,
                model.institution_id == institution_id,
                model.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def _list_tenant_entities(self, model, institution_id: UUID, limit: int, offset: int):
        result = await self.session.execute(
            select(model)
            .where(model.institution_id == institution_id, model.deleted_at.is_(None))
            .order_by(model.sequence, model.created_at)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
