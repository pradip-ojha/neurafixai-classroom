from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
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
    User,
)


class CoreRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_institution(self, institution_id: UUID) -> Institution | None:
        return await self.session.get(Institution, institution_id)

    async def get_settings(self, institution_id: UUID) -> InstitutionSettings | None:
        result = await self.session.execute(
            select(InstitutionSettings).where(InstitutionSettings.institution_id == institution_id)
        )
        return result.scalar_one_or_none()

    def add(self, entity: object) -> None:
        self.session.add(entity)

    async def flush(self) -> None:
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def list_users(self, institution_id: UUID, limit: int, offset: int) -> Sequence[User]:
        result = await self.session.execute(
            select(User)
            .where(User.institution_id == institution_id, User.deleted_at.is_(None))
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_branches(self, institution_id: UUID, limit: int, offset: int) -> Sequence[Branch]:
        return await self._list_tenant_entities(Branch, institution_id, limit, offset)

    async def list_academic_years(
        self,
        institution_id: UUID,
        limit: int,
        offset: int,
    ) -> Sequence[AcademicYear]:
        result = await self.session.execute(
            select(AcademicYear)
            .where(AcademicYear.institution_id == institution_id)
            .order_by(AcademicYear.starts_on.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_classes(self, institution_id: UUID, limit: int, offset: int) -> Sequence[SchoolClass]:
        return await self._list_tenant_entities(SchoolClass, institution_id, limit, offset)

    async def get_class(self, institution_id: UUID, class_id: UUID) -> SchoolClass | None:
        return await self._get_tenant_entity(SchoolClass, institution_id, class_id)

    async def list_sections(self, institution_id: UUID, limit: int, offset: int) -> Sequence[Section]:
        return await self._list_tenant_entities(Section, institution_id, limit, offset)

    async def get_section(self, institution_id: UUID, section_id: UUID) -> Section | None:
        return await self._get_tenant_entity(Section, institution_id, section_id)

    async def list_subjects(self, institution_id: UUID, limit: int, offset: int) -> Sequence[Subject]:
        return await self._list_tenant_entities(Subject, institution_id, limit, offset)

    async def list_students(self, institution_id: UUID, limit: int, offset: int) -> Sequence[Student]:
        return await self._list_tenant_entities(Student, institution_id, limit, offset)

    async def list_teachers(self, institution_id: UUID, limit: int, offset: int) -> Sequence[Teacher]:
        return await self._list_tenant_entities(Teacher, institution_id, limit, offset)

    async def list_parents(self, institution_id: UUID, limit: int, offset: int) -> Sequence[Parent]:
        return await self._list_tenant_entities(Parent, institution_id, limit, offset)

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
            .order_by(model.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

