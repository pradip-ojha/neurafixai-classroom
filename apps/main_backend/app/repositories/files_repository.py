from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FileAccessLog, FileObject


class FilesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, entity: object) -> None:
        self.session.add(entity)

    async def commit(self) -> None:
        await self.session.commit()

    async def get_file(self, institution_id: UUID, file_id: UUID) -> FileObject | None:
        result = await self.session.execute(
            select(FileObject).where(
                FileObject.id == file_id,
                FileObject.institution_id == institution_id,
                FileObject.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    def record_access(
        self,
        *,
        institution_id: UUID,
        file_object_id: UUID,
        actor_user_id: UUID | None,
        action: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        self.session.add(
            FileAccessLog(
                institution_id=institution_id,
                file_object_id=file_object_id,
                actor_user_id=actor_user_id,
                action=action,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
