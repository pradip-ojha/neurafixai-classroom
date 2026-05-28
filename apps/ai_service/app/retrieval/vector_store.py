from __future__ import annotations

from app.core.config import get_settings
from app.schemas.retrieval import RetrievalMatch, RetrievalSearchRequest


class VectorStore:
    async def search(self, payload: RetrievalSearchRequest) -> list[RetrievalMatch]:
        raise NotImplementedError


class PineconeVectorStore(VectorStore):
    def __init__(self) -> None:
        self.settings = get_settings()

    async def search(self, payload: RetrievalSearchRequest) -> list[RetrievalMatch]:
        if not self.settings.pinecone_api_key or not self.settings.pinecone_index:
            return []

        # Pinecone SDK integration starts when the ingestion pipeline begins real upserts.
        # The interface is intentionally strict so every future query carries tenant filters.
        return []
