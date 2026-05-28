from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ContentItem, ContentVersion


class ContentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, entity: object) -> None:
        self.session.add(entity)

    async def flush(self) -> None:
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def get_item(self, institution_id: UUID, content_item_id: UUID) -> ContentItem | None:
        result = await self.session.execute(
            select(ContentItem).where(
                ContentItem.id == content_item_id,
                ContentItem.institution_id == institution_id,
                ContentItem.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_items(self, institution_id: UUID, limit: int, offset: int) -> Sequence[ContentItem]:
        result = await self.session.execute(
            select(ContentItem)
            .where(ContentItem.institution_id == institution_id, ContentItem.deleted_at.is_(None))
            .order_by(ContentItem.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def next_version_number(self, institution_id: UUID, content_item_id: UUID) -> int:
        result = await self.session.execute(
            select(func.coalesce(func.max(ContentVersion.version_number), 0)).where(
                ContentVersion.institution_id == institution_id,
                ContentVersion.content_item_id == content_item_id,
            )
        )
        return int(result.scalar_one()) + 1
