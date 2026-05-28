from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIModelConfig, AISafetyEvent, AIUsageLog, InstitutionAILimit, PromptTemplate, PromptVersion
from app.repositories.ai_repository import AIRepository
from app.services.ai_service_client import AIServiceClient


class AIControlService:
    def __init__(self, session: AsyncSession, client: AIServiceClient | None = None) -> None:
        self.repo = AIRepository(session)
        self.client = client or AIServiceClient()

    async def create_model_config(self, institution_id: UUID, **values) -> AIModelConfig:
        if values.get("is_default"):
            await self.repo.clear_default_model_config(institution_id, values["task_type"])
        config = AIModelConfig(institution_id=institution_id, **values)
        self.repo.add(config)
        await self.repo.commit()
        return config

    async def get_or_create_limits(self, institution_id: UUID) -> InstitutionAILimit:
        limits = await self.repo.get_limits(institution_id)
        if limits:
            return limits
        limits = InstitutionAILimit(institution_id=institution_id)
        self.repo.add(limits)
        await self.repo.commit()
        return limits

    async def update_limits(self, institution_id: UUID, **values) -> InstitutionAILimit:
        limits = await self.get_or_create_limits(institution_id)
        for key, value in values.items():
            if value is not None:
                setattr(limits, key, value)
        await self.repo.commit()
        return limits

    async def create_prompt_template(self, institution_id: UUID, actor_user_id: UUID, **values) -> PromptTemplate:
        version_values = {
            "system_prompt": values.pop("system_prompt"),
            "user_prompt_template": values.pop("user_prompt_template"),
            "model_defaults": values.pop("model_defaults"),
        }
        template = PromptTemplate(institution_id=institution_id, **values)
        self.repo.add(template)
        await self.repo.flush()
        version = PromptVersion(
            institution_id=institution_id,
            prompt_template_id=template.id,
            version_number=1,
            created_by=actor_user_id,
            **version_values,
        )
        self.repo.add(version)
        await self.repo.flush()
        template.active_version_id = version.id
        await self.repo.commit()
        return template

    async def generate_text(
        self,
        *,
        institution_id: UUID,
        user_id: UUID,
        request_id: str,
        prompt: str,
        feature: str,
        model_config_id: UUID | None,
        metadata: dict | None,
    ) -> dict:
        limits = await self.get_or_create_limits(institution_id)
        if not limits.is_enabled:
            await self._record_safety_event(institution_id, user_id, feature, "quota", "medium", "blocked")
            raise HTTPException(status.HTTP_403_FORBIDDEN, "AI is disabled for this institution")

        used_tokens, used_cost = await self.repo.usage_for_day(institution_id, datetime.now(timezone.utc).date())
        if used_tokens >= limits.daily_token_limit or used_cost >= limits.daily_cost_limit_cents:
            await self._record_safety_event(institution_id, user_id, feature, "quota", "high", "blocked")
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Daily AI limit reached")

        config = None
        if model_config_id:
            config = await self.repo.get_model_config(institution_id, model_config_id)
        else:
            config = await self.repo.get_default_model_config(institution_id, feature)
        if not config:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "AI model config not found")

        response = await self.client.generate_text(
            {
                "institution_id": str(institution_id),
                "user_id": str(user_id),
                "feature": feature,
                "prompt": prompt,
                "provider": config.provider,
                "model_name": config.model_name,
                "max_output_tokens": config.max_output_tokens,
                "temperature": float(config.temperature),
                "metadata": metadata or {},
            },
            request_id,
        )
        usage = response.get("usage", {})
        total_tokens = int(usage.get("total_tokens", 0))
        prompt_tokens = int(usage.get("prompt_tokens", 0))
        completion_tokens = int(usage.get("completion_tokens", 0))
        estimated_cost_cents = int(usage.get("estimated_cost_cents", 0))
        self.repo.add(
            AIUsageLog(
                institution_id=institution_id,
                user_id=user_id,
                request_id=request_id,
                feature=feature,
                provider=config.provider,
                model_name=config.model_name,
                usage_date=datetime.now(timezone.utc).date(),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_cents=estimated_cost_cents,
                latency_ms=response.get("latency_ms"),
                metadata_json={"model_config_id": str(config.id), **(metadata or {})},
            )
        )
        safety = response.get("safety", {})
        if safety.get("flagged"):
            await self._record_safety_event(
                institution_id,
                user_id,
                feature,
                safety.get("category", "provider_flag"),
                safety.get("severity", "medium"),
                safety.get("action", "logged"),
                commit=False,
            )
        await self.repo.commit()
        return {
            "text": response["text"],
            "provider": config.provider,
            "model_name": config.model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_cents": estimated_cost_cents,
            "latency_ms": response.get("latency_ms"),
        }

    async def _record_safety_event(
        self,
        institution_id: UUID,
        user_id: UUID,
        feature: str,
        category: str,
        severity: str,
        action: str,
        *,
        commit: bool = True,
    ) -> None:
        self.repo.add(
            AISafetyEvent(
                institution_id=institution_id,
                user_id=user_id,
                feature=feature,
                category=category,
                severity=severity,
                action=action,
            )
        )
        if commit:
            await self.repo.commit()
