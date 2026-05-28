from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIConversation, AIMessage, AIMessageCitation


class TutorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, entity: object) -> None:
        self.session.add(entity)

    async def flush(self) -> None:
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def list_conversations(self, institution_id: UUID, user_id: UUID, limit: int, offset: int) -> Sequence[AIConversation]:
        result = await self.session.execute(
            select(AIConversation)
            .where(
                AIConversation.institution_id == institution_id,
                AIConversation.user_id == user_id,
                AIConversation.archived_at.is_(None),
            )
            .order_by(AIConversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_conversation(self, institution_id: UUID, user_id: UUID, conversation_id: UUID) -> AIConversation | None:
        result = await self.session.execute(
            select(AIConversation).where(
                AIConversation.id == conversation_id,
                AIConversation.institution_id == institution_id,
                AIConversation.user_id == user_id,
                AIConversation.archived_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_messages(self, institution_id: UUID, conversation_id: UUID, limit: int, offset: int) -> Sequence[AIMessage]:
        result = await self.session.execute(
            select(AIMessage)
            .where(AIMessage.institution_id == institution_id, AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
