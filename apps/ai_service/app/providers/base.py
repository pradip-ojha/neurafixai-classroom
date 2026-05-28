from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProviderTextResponse:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_cents: int = 0


class AIProvider(ABC):
    @abstractmethod
    async def generate_text(self, *, prompt: str, metadata: dict[str, Any]) -> ProviderTextResponse:
        raise NotImplementedError

    @abstractmethod
    async def generate_json(self, *, prompt: str, metadata: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def generate_stream(self, *, prompt: str, metadata: dict[str, Any]) -> AsyncIterator[str]:
        raise NotImplementedError

    @abstractmethod
    async def create_embedding(self, *, text: str, metadata: dict[str, Any]) -> list[float]:
        raise NotImplementedError

    @abstractmethod
    async def moderate_content(self, *, text: str, metadata: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
