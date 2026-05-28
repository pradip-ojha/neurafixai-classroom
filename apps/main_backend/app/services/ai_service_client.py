from __future__ import annotations

import httpx

from app.core.config import get_settings


class AIServiceClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_text(self, payload: dict, request_id: str | None) -> dict:
        headers = {
            "X-Internal-Service-Token": self.settings.ai_internal_service_token,
        }
        if request_id:
            headers["X-Request-ID"] = request_id
        async with httpx.AsyncClient(base_url=self.settings.ai_service_internal_url, timeout=45.0) as client:
            response = await client.post("/api/v1/internal/generate/text", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
