from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FileUploadUrlRequest(BaseModel):
    original_filename: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=160)
    size_bytes: int = Field(gt=0, le=104_857_600)
    checksum: str | None = Field(default=None, max_length=160)
    module: str = Field(default="general", min_length=1, max_length=80)
    entity_id: UUID | None = None
    visibility: str = Field(default="private", pattern="^(private|institution|public)$")


class FileObjectData(BaseModel):
    id: UUID
    institution_id: UUID
    owner_user_id: UUID | None
    bucket: str
    object_key: str
    original_filename: str
    mime_type: str
    size_bytes: int
    checksum: str | None
    visibility: str
    scan_status: str
    processing_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SignedFileUrlData(BaseModel):
    file: FileObjectData
    url: str
    expires_in_seconds: int
