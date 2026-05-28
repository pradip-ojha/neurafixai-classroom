from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class AIModelConfigCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    provider: str = Field(default="openai_compatible", max_length=80)
    model_name: str = Field(min_length=1, max_length=160)
    task_type: str = Field(min_length=1, max_length=80)
    max_output_tokens: int = Field(default=1024, ge=1, le=8192)
    temperature: Decimal = Field(default=Decimal("0.2"), ge=0, le=2)
    is_default: bool = False
    settings_json: dict | None = None


class AIModelConfigData(AIModelConfigCreateRequest):
    id: UUID
    institution_id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class InstitutionAILimitUpdateRequest(BaseModel):
    daily_token_limit: int | None = Field(default=None, ge=1)
    monthly_token_limit: int | None = Field(default=None, ge=1)
    daily_cost_limit_cents: int | None = Field(default=None, ge=0)
    monthly_cost_limit_cents: int | None = Field(default=None, ge=0)
    is_enabled: bool | None = None


class InstitutionAILimitData(BaseModel):
    id: UUID
    institution_id: UUID
    daily_token_limit: int
    monthly_token_limit: int
    daily_cost_limit_cents: int
    monthly_cost_limit_cents: int
    is_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PromptTemplateCreateRequest(BaseModel):
    slug: str = Field(min_length=2, max_length=120)
    name: str = Field(min_length=2, max_length=160)
    feature: str = Field(min_length=1, max_length=80)
    description: str | None = None
    system_prompt: str = Field(min_length=1)
    user_prompt_template: str = Field(min_length=1)
    model_defaults: dict | None = None


class PromptTemplateData(BaseModel):
    id: UUID
    institution_id: UUID | None
    slug: str
    name: str
    feature: str
    description: str | None
    active_version_id: UUID | None
    is_system: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AITextGenerationRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=6000)
    feature: str = Field(default="ai_content.generate", max_length=80)
    model_config_id: UUID | None = None
    metadata: dict | None = None


class AITextGenerationData(BaseModel):
    text: str
    provider: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_cents: int
    latency_ms: int | None
