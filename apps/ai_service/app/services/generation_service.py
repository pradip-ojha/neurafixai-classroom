from __future__ import annotations

import time

from fastapi import HTTPException, status

from app.providers.factory import get_provider
from app.safety.filters import evaluate_prompt_safety
from app.schemas.generation import SafetyData, TextGenerationRequest, TextGenerationResponse, UsageData


class GenerationService:
    async def generate_text(self, payload: TextGenerationRequest) -> TextGenerationResponse:
        started = time.perf_counter()
        safety = evaluate_prompt_safety(payload.prompt)
        if safety["flagged"] and safety["action"] == "blocked":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Prompt failed AI safety checks")

        provider = get_provider(payload.provider)
        provider_response = await provider.generate_text(
            prompt=payload.prompt,
            metadata={
                "institution_id": payload.institution_id,
                "user_id": payload.user_id,
                "feature": payload.feature,
                "model_name": payload.model_name,
                "max_output_tokens": payload.max_output_tokens,
                "temperature": payload.temperature,
                **payload.metadata,
            },
        )
        provider_safety = await provider.moderate_content(
            text=provider_response.text,
            metadata={"institution_id": payload.institution_id, "feature": payload.feature},
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        flagged = bool(provider_safety.get("flagged", False))
        return TextGenerationResponse(
            text=provider_response.text,
            usage=UsageData(
                prompt_tokens=provider_response.prompt_tokens,
                completion_tokens=provider_response.completion_tokens,
                total_tokens=provider_response.total_tokens,
                estimated_cost_cents=provider_response.estimated_cost_cents,
            ),
            safety=SafetyData(
                flagged=flagged,
                category="provider_moderation" if flagged else None,
                severity="medium" if flagged else None,
                action="logged" if flagged else "allowed",
            ),
            latency_ms=latency_ms,
        )
