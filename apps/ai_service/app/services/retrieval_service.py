from __future__ import annotations

from fastapi import HTTPException, status

from app.retrieval.vector_store import PineconeVectorStore
from app.schemas.retrieval import RetrievalSearchRequest, RetrievalSearchResponse


class RetrievalService:
    def __init__(self) -> None:
        self.vector_store = PineconeVectorStore()

    async def search(self, payload: RetrievalSearchRequest) -> RetrievalSearchResponse:
        filters = payload.filters.model_dump(exclude_none=True)
        if not payload.namespace.startswith(f"institution_{payload.filters.institution_id}"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Vector namespace does not match institution filter")
        matches = await self.vector_store.search(payload)
        return RetrievalSearchResponse(matches=matches, namespace=payload.namespace, filters=filters)
