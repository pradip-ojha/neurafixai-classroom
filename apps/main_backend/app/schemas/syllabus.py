from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SyllabusChapterCreateRequest(BaseModel):
    class_id: UUID
    subject_id: UUID
    name: str = Field(min_length=1, max_length=180)
    description: str | None = None
    sequence: int = Field(default=0, ge=0)


class SyllabusChapterData(SyllabusChapterCreateRequest):
    id: UUID
    institution_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class SyllabusTopicCreateRequest(BaseModel):
    chapter_id: UUID
    name: str = Field(min_length=1, max_length=180)
    description: str | None = None
    sequence: int = Field(default=0, ge=0)


class SyllabusTopicData(SyllabusTopicCreateRequest):
    id: UUID
    institution_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class SyllabusSubtopicCreateRequest(BaseModel):
    topic_id: UUID
    name: str = Field(min_length=1, max_length=180)
    description: str | None = None
    sequence: int = Field(default=0, ge=0)


class SyllabusSubtopicData(SyllabusSubtopicCreateRequest):
    id: UUID
    institution_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class LearningObjectiveCreateRequest(BaseModel):
    chapter_id: UUID | None = None
    topic_id: UUID | None = None
    subtopic_id: UUID | None = None
    text: str = Field(min_length=1)
    sequence: int = Field(default=0, ge=0)


class LearningObjectiveData(LearningObjectiveCreateRequest):
    id: UUID
    institution_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
