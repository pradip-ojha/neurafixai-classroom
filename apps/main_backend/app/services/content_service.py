from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ContentApproval, ContentItem, ContentTag, ContentVersion
from app.repositories.content_repository import ContentRepository


class ContentService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ContentRepository(session)

    async def create_item(
        self,
        institution_id: UUID,
        owner_user_id: UUID,
        *,
        body: str | None,
        summary: str | None,
        tags: list[str],
        **values,
    ) -> ContentItem:
        item = ContentItem(institution_id=institution_id, owner_user_id=owner_user_id, **values)
        self.repo.add(item)
        await self.repo.flush()
        version = ContentVersion(
            institution_id=institution_id,
            content_item_id=item.id,
            version_number=1,
            body=body,
            summary=summary,
            created_by=owner_user_id,
        )
        self.repo.add(version)
        for tag in {tag.strip().lower() for tag in tags if tag.strip()}:
            self.repo.add(ContentTag(institution_id=institution_id, content_item_id=item.id, tag=tag[:80]))
        await self.repo.flush()
        item.current_version_id = version.id
        await self.repo.commit()
        return item

    async def create_version(
        self,
        institution_id: UUID,
        actor_user_id: UUID,
        content_item_id: UUID,
        **values,
    ) -> ContentItem:
        item = await self.repo.get_item(institution_id, content_item_id)
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Content item not found")
        version = ContentVersion(
            institution_id=institution_id,
            content_item_id=item.id,
            version_number=await self.repo.next_version_number(institution_id, item.id),
            created_by=actor_user_id,
            **values,
        )
        self.repo.add(version)
        await self.repo.flush()
        item.current_version_id = version.id
        item.status = "draft"
        await self.repo.commit()
        return item

    async def review_item(
        self,
        institution_id: UUID,
        reviewer_user_id: UUID,
        content_item_id: UUID,
        *,
        status_value: str,
        comment: str | None,
    ) -> ContentItem:
        item = await self.repo.get_item(institution_id, content_item_id)
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Content item not found")
        item.status = status_value
        self.repo.add(
            ContentApproval(
                institution_id=institution_id,
                content_item_id=item.id,
                status=status_value,
                reviewer_user_id=reviewer_user_id,
                comment=comment,
            )
        )
        await self.repo.commit()
        return item
