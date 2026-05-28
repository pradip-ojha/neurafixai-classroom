from pydantic import BaseModel, Field


class TextGenerationRequest(BaseModel):
    institution_id: str
    user_id: str
    feature: str = Field(min_length=1, max_length=80)
    prompt: str = Field(min_length=1, max_length=6000)
    provider: str = Field(default="openai_compatible", max_length=80)
    model_name: str = Field(min_length=1, max_length=160)
    max_output_tokens: int = Field(default=1024, ge=1, le=8192)
    temperature: float = Field(default=0.2, ge=0, le=2)
    metadata: dict = Field(default_factory=dict)


class UsageData(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_cents: int = 0


class SafetyData(BaseModel):
    flagged: bool = False
    category: str | None = None
    severity: str | None = None
    action: str = "allowed"


class TextGenerationResponse(BaseModel):
    text: str
    usage: UsageData
    safety: SafetyData
    latency_ms: int | None = None
