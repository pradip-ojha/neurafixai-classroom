from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TutorConversationCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    class_id: UUID | None = None
    subject_id: UUID | None = None
    chapter_id: UUID | None = None
    topic_id: UUID | None = None
    metadata_json: dict | None = None


class TutorConversationData(BaseModel):
    id: UUID
    institution_id: UUID
    user_id: UUID
    title: str | None
    feature: str
    class_id: UUID | None
    subject_id: UUID | None
    chapter_id: UUID | None
    topic_id: UUID | None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None

    model_config = {"from_attributes": True}


class TutorMessageData(BaseModel):
    id: UUID
    institution_id: UUID
    conversation_id: UUID
    user_id: UUID | None
    role: str
    content: str
    provider: str | None
    model_name: str | None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_cents: int
    latency_ms: int | None
    safety_status: str
    metadata_json: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TutorCitationData(BaseModel):
    id: UUID
    institution_id: UUID
    message_id: UUID
    knowledge_chunk_id: UUID
    rank: int
    citation_text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TutorAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None
    title: str | None = Field(default=None, max_length=255)
    knowledge_base_id: UUID | None = None
    class_id: UUID | None = None
    subject_id: UUID | None = None
    chapter_id: UUID | None = None
    topic_id: UUID | None = None
    model_config_id: UUID | None = None
    metadata: dict | None = None


class TutorAskData(BaseModel):
    conversation: TutorConversationData
    user_message: TutorMessageData
    assistant_message: TutorMessageData
    citations: list[TutorCitationData]
