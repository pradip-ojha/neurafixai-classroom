from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.jobs import BackgroundJobData


class KnowledgeBaseCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    slug: str = Field(min_length=2, max_length=120)
    description: str | None = None


class KnowledgeBaseData(BaseModel):
    id: UUID
    institution_id: UUID
    name: str
    slug: str
    description: str | None
    vector_namespace: str
    is_active: bool
    created_by: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeDocumentCreateRequest(BaseModel):
    knowledge_base_id: UUID
    title: str = Field(min_length=1, max_length=255)
    source_type: str = Field(min_length=1, max_length=60)
    file_object_id: UUID | None = None
    content_item_id: UUID | None = None
    class_id: UUID | None = None
    subject_id: UUID | None = None
    chapter_id: UUID | None = None
    topic_id: UUID | None = None
    subtopic_id: UUID | None = None
    language: str = Field(default="en", max_length=20)
    visibility: str = Field(default="institution", pattern="^(private|institution|public)$")
    approved: bool = False
    metadata_json: dict | None = None


class KnowledgeDocumentData(BaseModel):
    id: UUID
    institution_id: UUID
    knowledge_base_id: UUID
    file_object_id: UUID | None
    content_item_id: UUID | None
    title: str
    source_type: str
    class_id: UUID | None
    subject_id: UUID | None
    chapter_id: UUID | None
    topic_id: UUID | None
    subtopic_id: UUID | None
    language: str
    visibility: str
    approved: bool
    index_status: str
    chunk_count: int
    created_by: UUID | None
    created_at: datetime
    indexed_at: datetime | None

    model_config = {"from_attributes": True}


class KnowledgeDocumentIngestData(BaseModel):
    document: KnowledgeDocumentData
    job: BackgroundJobData


class KnowledgeChunkData(BaseModel):
    id: UUID
    institution_id: UUID
    knowledge_base_id: UUID
    knowledge_document_id: UUID
    chunk_index: int
    text: str
    token_count: int | None
    vector_namespace: str
    vector_id: str | None
    embedding_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RetrievalSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    feature: str = Field(default="ai_tutor.use", max_length=80)
    knowledge_base_id: UUID | None = None
    class_id: UUID | None = None
    subject_id: UUID | None = None
    chapter_id: UUID | None = None
    topic_id: UUID | None = None
    approved_only: bool = True
    limit: int = Field(default=5, ge=1, le=20)


class RetrievalSearchData(BaseModel):
    chunks: list[KnowledgeChunkData]
    filters: dict
