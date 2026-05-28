from pydantic import BaseModel, Field


class RetrievalFilter(BaseModel):
    institution_id: str
    knowledge_base_id: str | None = None
    class_id: str | None = None
    subject_id: str | None = None
    chapter_id: str | None = None
    topic_id: str | None = None
    subtopic_id: str | None = None
    approved: bool = True
    visibility: list[str] = Field(default_factory=lambda: ["institution", "public"])


class RetrievalSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    namespace: str
    filters: RetrievalFilter
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievalMatch(BaseModel):
    chunk_id: str
    score: float
    metadata: dict


class RetrievalSearchResponse(BaseModel):
    matches: list[RetrievalMatch]
    namespace: str
    filters: dict
