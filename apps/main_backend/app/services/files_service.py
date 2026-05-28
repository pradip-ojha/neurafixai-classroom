from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import FileObject
from app.repositories.files_repository import FilesRepository
from app.services.storage_service import StorageService


class FilesService:
    def __init__(self, session: AsyncSession, storage: StorageService | None = None) -> None:
        self.repo = FilesRepository(session)
        self.storage = storage or StorageService()
        self.settings = get_settings()

    async def create_upload_url(
        self,
        institution_id: UUID,
        owner_user_id: UUID,
        *,
        original_filename: str,
        mime_type: str,
        size_bytes: int,
        checksum: str | None,
        module: str,
        entity_id: UUID | None,
        visibility: str,
    ) -> tuple[FileObject, str, int]:
        file_id = uuid4()
        object_key = self.storage.build_object_key(
            institution_id=institution_id,
            module=module,
            entity_id=entity_id,
            file_id=file_id,
            filename=original_filename,
        )
        file_object = FileObject(
            id=file_id,
            institution_id=institution_id,
            owner_user_id=owner_user_id,
            bucket=self.settings.object_storage_bucket,
            object_key=object_key,
            original_filename=original_filename,
            mime_type=mime_type,
            size_bytes=size_bytes,
            checksum=checksum,
            visibility=visibility,
        )
        self.repo.add(file_object)
        self.repo.record_access(
            institution_id=institution_id,
            file_object_id=file_id,
            actor_user_id=owner_user_id,
            action="upload_url.created",
            ip_address=None,
            user_agent=None,
        )
        await self.repo.commit()
        return file_object, self.storage.signed_url(method="PUT", object_key=object_key), self.settings.signed_url_expiry_seconds

    async def create_download_url(
        self,
        institution_id: UUID,
        actor_user_id: UUID,
        file_id: UUID,
        *,
        ip_address: str | None,
        user_agent: str | None,
    ) -> tuple[FileObject, str, int]:
        file_object = await self.repo.get_file(institution_id, file_id)
        if not file_object:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")

        self.repo.record_access(
            institution_id=institution_id,
            file_object_id=file_object.id,
            actor_user_id=actor_user_id,
            action="download_url.created",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.repo.commit()
        return (
            file_object,
            self.storage.signed_url(method="GET", object_key=file_object.object_key),
            self.settings.signed_url_expiry_seconds,
        )
