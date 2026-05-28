from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIModelConfig, AIUsageLog, InstitutionAILimit, PromptTemplate, PromptVersion


class AIRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, entity: object) -> None:
        self.session.add(entity)

    async def flush(self) -> None:
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def list_model_configs(self, institution_id: UUID) -> list[AIModelConfig]:
        result = await self.session.execute(
            select(AIModelConfig)
            .where(AIModelConfig.institution_id == institution_id, AIModelConfig.deleted_at.is_(None))
            .order_by(AIModelConfig.is_default.desc(), AIModelConfig.name)
        )
        return list(result.scalars().all())

    async def get_model_config(self, institution_id: UUID, config_id: UUID) -> AIModelConfig | None:
        result = await self.session.execute(
            select(AIModelConfig).where(
                AIModelConfig.id == config_id,
                AIModelConfig.institution_id == institution_id,
                AIModelConfig.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_default_model_config(self, institution_id: UUID, task_type: str) -> AIModelConfig | None:
        result = await self.session.execute(
            select(AIModelConfig).where(
                AIModelConfig.institution_id == institution_id,
                AIModelConfig.task_type == task_type,
                AIModelConfig.is_default.is_(True),
                AIModelConfig.is_active.is_(True),
                AIModelConfig.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def clear_default_model_config(self, institution_id: UUID, task_type: str) -> None:
        await self.session.execute(
            update(AIModelConfig)
            .where(AIModelConfig.institution_id == institution_id, AIModelConfig.task_type == task_type)
            .values(is_default=False)
        )

    async def get_limits(self, institution_id: UUID) -> InstitutionAILimit | None:
        result = await self.session.execute(
            select(InstitutionAILimit).where(InstitutionAILimit.institution_id == institution_id)
        )
        return result.scalar_one_or_none()

    async def usage_for_day(self, institution_id: UUID, usage_date: date) -> tuple[int, int]:
        result = await self.session.execute(
            select(
                func.coalesce(func.sum(AIUsageLog.total_tokens), 0),
                func.coalesce(func.sum(AIUsageLog.estimated_cost_cents), 0),
            ).where(AIUsageLog.institution_id == institution_id, AIUsageLog.usage_date == usage_date)
        )
        row = result.one()
        return int(row[0]), int(row[1])

    async def list_prompt_templates(self, institution_id: UUID) -> list[PromptTemplate]:
        result = await self.session.execute(
            select(PromptTemplate)
            .where(
                PromptTemplate.deleted_at.is_(None),
                (PromptTemplate.institution_id == institution_id) | (PromptTemplate.institution_id.is_(None)),
            )
            .order_by(PromptTemplate.feature, PromptTemplate.name)
        )
        return list(result.scalars().all())

    async def next_prompt_version(self, template_id: UUID) -> int:
        result = await self.session.execute(
            select(func.coalesce(func.max(PromptVersion.version_number), 0)).where(
                PromptVersion.prompt_template_id == template_id
            )
        )
        return int(result.scalar_one()) + 1
