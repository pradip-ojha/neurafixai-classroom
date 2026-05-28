from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EmbeddingJob, KnowledgeBase, KnowledgeChunk, KnowledgeDocument, RetrievalLog
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.jobs_service import JobsService


class KnowledgeService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = KnowledgeRepository(session)
        self.jobs = JobsService(session)

    async def create_base(self, institution_id: UUID, actor_user_id: UUID, **values) -> KnowledgeBase:
        slug = values["slug"].strip().lower()
        base = KnowledgeBase(
            institution_id=institution_id,
            created_by=actor_user_id,
            vector_namespace=f"institution_{institution_id}_{slug}",
            **{**values, "slug": slug},
        )
        self.repo.add(base)
        await self.repo.commit()
        return base

    async def create_document(self, institution_id: UUID, actor_user_id: UUID, **values) -> KnowledgeDocument:
        if not await self.repo.get_base(institution_id, values["knowledge_base_id"]):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Knowledge base not found")
        if not values.get("file_object_id") and not values.get("content_item_id"):
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Document must reference a file or content item")
        document = KnowledgeDocument(institution_id=institution_id, created_by=actor_user_id, **values)
        self.repo.add(document)
        await self.repo.commit()
        return document

    async def ingest_document(
        self,
        institution_id: UUID,
        actor_user_id: UUID,
        document_id: UUID,
        *,
        idempotency_key: str | None,
    ):
        document = await self.repo.get_document(institution_id, document_id)
        if not document:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Knowledge document not found")
        document.index_status = "queued"
        await self.repo.flush()
        job = await self.jobs.create_and_enqueue(
            institution_id=institution_id,
            actor_user_id=actor_user_id,
            job_type="rag.document_ingestion",
            queue_name="rag_ingestion",
            task_name="rag.ingest_document",
            input_payload={"knowledge_document_id": str(document.id)},
            idempotency_key=idempotency_key,
            max_retries=3,
        )
        existing_embedding_job = await self.repo.get_embedding_job(institution_id, document.id)
        if not existing_embedding_job:
            self.repo.add(
                EmbeddingJob(
                    institution_id=institution_id,
                    knowledge_document_id=document.id,
                    background_job_id=job.id,
                    status="queued",
                )
            )
            await self.repo.commit()
        return document, job

    async def mark_document_indexed_placeholder(self, document_id: UUID) -> None:
        document = await self.repo.session.get(KnowledgeDocument, document_id)
        if not document:
            raise RuntimeError(f"Knowledge document {document_id} was not found")
        base = await self.repo.session.get(KnowledgeBase, document.knowledge_base_id)
        if not base:
            raise RuntimeError(f"Knowledge base {document.knowledge_base_id} was not found")
        document.index_status = "indexed"
        document.indexed_at = datetime.now(timezone.utc)
        if document.chunk_count == 0:
            chunk = KnowledgeChunk(
                institution_id=document.institution_id,
                knowledge_base_id=document.knowledge_base_id,
                knowledge_document_id=document.id,
                chunk_index=0,
                text=f"Placeholder indexed chunk for {document.title}.",
                token_count=5,
                vector_namespace=base.vector_namespace,
                vector_id=f"{document.id}:0",
                embedding_status="indexed",
                metadata_json={"placeholder": True},
            )
            self.repo.add(chunk)
            document.chunk_count = 1
        embedding_job = await self.repo.get_embedding_job(document.institution_id, document.id)
        if embedding_job:
            embedding_job.status = "completed"
            embedding_job.chunks_total = document.chunk_count
            embedding_job.chunks_completed = document.chunk_count
        await self.repo.commit()

    async def search(
        self,
        institution_id: UUID,
        user_id: UUID,
        *,
        query: str,
        feature: str,
        limit: int,
        **filters,
    ):
        chunks = list(await self.repo.keyword_search_chunks(institution_id, query, filters, limit))
        self.repo.add(
            RetrievalLog(
                institution_id=institution_id,
                user_id=user_id,
                feature=feature,
                query=query,
                filters_json=filters,
                result_chunk_ids=[str(chunk.id) for chunk in chunks],
            )
        )
        await self.repo.commit()
        return chunks, filters
