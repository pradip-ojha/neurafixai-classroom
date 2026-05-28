from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ContentItemCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=60)
    visibility: str = Field(default="institution", pattern="^(private|institution|public)$")
    class_id: UUID | None = None
    subject_id: UUID | None = None
    chapter_id: UUID | None = None
    topic_id: UUID | None = None
    subtopic_id: UUID | None = None
    body: str | None = None
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)


class ContentItemData(BaseModel):
    id: UUID
    institution_id: UUID
    title: str
    content_type: str
    status: str
    visibility: str
    class_id: UUID | None
    subject_id: UUID | None
    chapter_id: UUID | None
    topic_id: UUID | None
    subtopic_id: UUID | None
    owner_user_id: UUID | None
    current_version_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentVersionCreateRequest(BaseModel):
    body: str | None = None
    summary: str | None = None
    metadata_json: dict | None = None


class ContentApprovalRequest(BaseModel):
    status: str = Field(pattern="^(approved|rejected|needs_changes)$")
    comment: str | None = None
