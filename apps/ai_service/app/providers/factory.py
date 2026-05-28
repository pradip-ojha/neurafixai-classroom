from app.providers.base import AIProvider
from app.providers.openai_compatible import OpenAICompatibleProvider


def get_provider(provider_name: str) -> AIProvider:
    if provider_name == "openai_compatible":
        return OpenAICompatibleProvider()
    raise ValueError(f"Unsupported AI provider: {provider_name}")
