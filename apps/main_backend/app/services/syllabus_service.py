from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LearningObjective, SyllabusChapter, SyllabusSubtopic, SyllabusTopic
from app.repositories.core_repository import CoreRepository
from app.repositories.syllabus_repository import SyllabusRepository


class SyllabusService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = SyllabusRepository(session)
        self.core_repo = CoreRepository(session)

    async def create_chapter(self, institution_id: UUID, *, class_id: UUID, subject_id: UUID, **values) -> SyllabusChapter:
        if not await self.core_repo.get_class(institution_id, class_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Class not found")
        chapter = SyllabusChapter(institution_id=institution_id, class_id=class_id, subject_id=subject_id, **values)
        self.repo.add(chapter)
        await self.repo.commit()
        return chapter

    async def create_topic(self, institution_id: UUID, *, chapter_id: UUID, **values) -> SyllabusTopic:
        if not await self.repo.get_chapter(institution_id, chapter_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
        topic = SyllabusTopic(institution_id=institution_id, chapter_id=chapter_id, **values)
        self.repo.add(topic)
        await self.repo.commit()
        return topic

    async def create_subtopic(self, institution_id: UUID, *, topic_id: UUID, **values) -> SyllabusSubtopic:
        if not await self.repo.get_topic(institution_id, topic_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")
        subtopic = SyllabusSubtopic(institution_id=institution_id, topic_id=topic_id, **values)
        self.repo.add(subtopic)
        await self.repo.commit()
        return subtopic

    async def create_objective(self, institution_id: UUID, **values) -> LearningObjective:
        if not any(values.get(key) for key in ("chapter_id", "topic_id", "subtopic_id")):
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Objective must attach to syllabus scope")
        objective = LearningObjective(institution_id=institution_id, **values)
        self.repo.add(objective)
        await self.repo.commit()
        return objective
