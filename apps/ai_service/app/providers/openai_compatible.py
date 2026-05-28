from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.config import get_settings
from app.providers.base import AIProvider, ProviderTextResponse


class LocalDevelopmentProvider(AIProvider):
    async def generate_text(self, *, prompt: str, metadata: dict[str, Any]) -> ProviderTextResponse:
        text = "AI provider is not configured. Local development fallback returned this placeholder response."
        return ProviderTextResponse(
            text=text,
            prompt_tokens=max(1, len(prompt.split())),
            completion_tokens=len(text.split()),
            total_tokens=max(1, len(prompt.split())) + len(text.split()),
        )

    async def generate_json(self, *, prompt: str, metadata: dict[str, Any]) -> dict[str, Any]:
        return {"text": (await self.generate_text(prompt=prompt, metadata=metadata)).text}

    async def generate_stream(self, *, prompt: str, metadata: dict[str, Any]) -> AsyncIterator[str]:
        yield (await self.generate_text(prompt=prompt, metadata=metadata)).text

    async def create_embedding(self, *, text: str, metadata: dict[str, Any]) -> list[float]:
        return [0.0] * 8

    async def moderate_content(self, *, text: str, metadata: dict[str, Any]) -> dict[str, Any]:
        return {"flagged": False}

class OpenAICompatibleProvider(AIProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_text(self, *, prompt: str, metadata: dict[str, Any]) -> ProviderTextResponse:
        if not self.settings.openai_compatible_api_key or not self.settings.openai_compatible_base_url:
            return await LocalDevelopmentProvider().generate_text(prompt=prompt, metadata=metadata)

        model_name = metadata.get("model_name") or self.settings.openai_compatible_default_model
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": metadata.get("temperature", 0.2),
            "max_tokens": metadata.get("max_output_tokens", 1024),
        }
        async with httpx.AsyncClient(base_url=self.settings.openai_compatible_base_url.rstrip("/"), timeout=45.0) as client:
            response = await client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.openai_compatible_api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        usage = data.get("usage", {})
        return ProviderTextResponse(
            text=data["choices"][0]["message"]["content"],
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
            total_tokens=int(usage.get("total_tokens", 0)),
        )

    async def generate_json(self, *, prompt: str, metadata: dict[str, Any]) -> dict[str, Any]:
        return {"text": (await self.generate_text(prompt=prompt, metadata=metadata)).text}

    async def generate_stream(self, *, prompt: str, metadata: dict[str, Any]) -> AsyncIterator[str]:
        yield (await self.generate_text(prompt=prompt, metadata=metadata)).text

    async def create_embedding(self, *, text: str, metadata: dict[str, Any]) -> list[float]:
        if not self.settings.openai_compatible_api_key or not self.settings.openai_compatible_base_url:
            return await LocalDevelopmentProvider().create_embedding(text=text, metadata=metadata)
        async with httpx.AsyncClient(base_url=self.settings.openai_compatible_base_url.rstrip("/"), timeout=45.0) as client:
            response = await client.post(
                "/embeddings",
                headers={"Authorization": f"Bearer {self.settings.openai_compatible_api_key}"},
                json={"model": metadata.get("embedding_model", "text-embedding-3-small"), "input": text},
            )
            response.raise_for_status()
            data = response.json()
        return list(data["data"][0]["embedding"])

    async def moderate_content(self, *, text: str, metadata: dict[str, Any]) -> dict[str, Any]:
        if not self.settings.openai_compatible_api_key or not self.settings.openai_compatible_base_url:
            return {"flagged": False}
        async with httpx.AsyncClient(base_url=self.settings.openai_compatible_base_url.rstrip("/"), timeout=20.0) as client:
            response = await client.post(
                "/moderations",
                headers={"Authorization": f"Bearer {self.settings.openai_compatible_api_key}"},
                json={"model": metadata.get("moderation_model", "omni-moderation-latest"), "input": text},
            )
            response.raise_for_status()
            data = response.json()
        result = data.get("results", [{}])[0]
        return {"flagged": bool(result.get("flagged")), "categories": result.get("categories", {})}
