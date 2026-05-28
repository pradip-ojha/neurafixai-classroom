from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EmbeddingJob, KnowledgeBase, KnowledgeChunk, KnowledgeDocument, RetrievalLog


class KnowledgeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, entity: object) -> None:
        self.session.add(entity)

    async def flush(self) -> None:
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def list_bases(self, institution_id: UUID, limit: int, offset: int) -> Sequence[KnowledgeBase]:
        result = await self.session.execute(
            select(KnowledgeBase)
            .where(KnowledgeBase.institution_id == institution_id, KnowledgeBase.deleted_at.is_(None))
            .order_by(KnowledgeBase.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_base(self, institution_id: UUID, knowledge_base_id: UUID) -> KnowledgeBase | None:
        result = await self.session.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.id == knowledge_base_id,
                KnowledgeBase.institution_id == institution_id,
                KnowledgeBase.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_documents(self, institution_id: UUID, limit: int, offset: int) -> Sequence[KnowledgeDocument]:
        result = await self.session.execute(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.institution_id == institution_id, KnowledgeDocument.deleted_at.is_(None))
            .order_by(KnowledgeDocument.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_document(self, institution_id: UUID, document_id: UUID) -> KnowledgeDocument | None:
        result = await self.session.execute(
            select(KnowledgeDocument).where(
                KnowledgeDocument.id == document_id,
                KnowledgeDocument.institution_id == institution_id,
                KnowledgeDocument.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_chunks(self, institution_id: UUID, document_id: UUID, limit: int, offset: int) -> Sequence[KnowledgeChunk]:
        result = await self.session.execute(
            select(KnowledgeChunk)
            .where(
                KnowledgeChunk.institution_id == institution_id,
                KnowledgeChunk.knowledge_document_id == document_id,
            )
            .order_by(KnowledgeChunk.chunk_index)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def keyword_search_chunks(
        self,
        institution_id: UUID,
        query: str,
        filters: dict,
        limit: int,
    ) -> Sequence[KnowledgeChunk]:
        conditions = [KnowledgeChunk.institution_id == institution_id, KnowledgeChunk.text.ilike(f"%{query}%")]
        if filters.get("knowledge_base_id"):
            conditions.append(KnowledgeChunk.knowledge_base_id == UUID(str(filters["knowledge_base_id"])))
        if filters.get("approved_only", True):
            conditions.append(KnowledgeDocument.approved.is_(True))
        result = await self.session.execute(
            select(KnowledgeChunk)
            .join(KnowledgeDocument, KnowledgeDocument.id == KnowledgeChunk.knowledge_document_id)
            .where(*conditions)
            .order_by(KnowledgeChunk.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_embedding_job(self, institution_id: UUID, document_id: UUID) -> EmbeddingJob | None:
        result = await self.session.execute(
            select(EmbeddingJob).where(
                EmbeddingJob.institution_id == institution_id,
                EmbeddingJob.knowledge_document_id == document_id,
            )
        )
        return result.scalar_one_or_none()
