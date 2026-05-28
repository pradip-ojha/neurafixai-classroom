from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AcademicYear,
    Branch,
    Institution,
    InstitutionSettings,
    Parent,
    SchoolClass,
    Section,
    Student,
    Subject,
    Teacher,
)
from app.repositories.core_repository import CoreRepository


class CoreService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = CoreRepository(session)

    async def get_institution(self, institution_id: UUID) -> Institution:
        institution = await self.repo.get_institution(institution_id)
        if not institution:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Institution not found")
        return institution

    async def update_institution(self, institution_id: UUID, *, name: str | None) -> Institution:
        institution = await self.get_institution(institution_id)
        if name is not None:
            institution.name = name.strip()
        await self.repo.commit()
        return institution

    async def get_or_create_settings(self, institution_id: UUID) -> InstitutionSettings:
        settings = await self.repo.get_settings(institution_id)
        if settings:
            return settings

        settings = InstitutionSettings(institution_id=institution_id)
        self.repo.add(settings)
        await self.repo.commit()
        return settings

    async def create_branch(self, institution_id: UUID, **values) -> Branch:
        branch = Branch(institution_id=institution_id, **values)
        return await self._persist(branch)

    async def create_academic_year(self, institution_id: UUID, **values) -> AcademicYear:
        year = AcademicYear(institution_id=institution_id, **values)
        return await self._persist(year)

    async def create_class(self, institution_id: UUID, **values) -> SchoolClass:
        school_class = SchoolClass(institution_id=institution_id, **values)
        return await self._persist(school_class)

    async def create_section(self, institution_id: UUID, *, class_id: UUID, **values) -> Section:
        if not await self.repo.get_class(institution_id, class_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Class not found")
        section = Section(institution_id=institution_id, class_id=class_id, **values)
        return await self._persist(section)

    async def create_subject(self, institution_id: UUID, **values) -> Subject:
        subject = Subject(institution_id=institution_id, **values)
        return await self._persist(subject)

    async def create_student(
        self,
        institution_id: UUID,
        *,
        current_class_id: UUID | None,
        current_section_id: UUID | None,
        **values,
    ) -> Student:
        if current_class_id and not await self.repo.get_class(institution_id, current_class_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Class not found")
        if current_section_id and not await self.repo.get_section(institution_id, current_section_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Section not found")

        student = Student(
            institution_id=institution_id,
            current_class_id=current_class_id,
            current_section_id=current_section_id,
            **values,
        )
        return await self._persist(student)

    async def create_teacher(self, institution_id: UUID, **values) -> Teacher:
        teacher = Teacher(institution_id=institution_id, **values)
        return await self._persist(teacher)

    async def create_parent(self, institution_id: UUID, **values) -> Parent:
        parent = Parent(institution_id=institution_id, **values)
        return await self._persist(parent)

    async def _persist(self, entity):
        self.repo.add(entity)
        await self.repo.commit()
        return entity

