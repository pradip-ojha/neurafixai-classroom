from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = Field(default="local", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    ai_internal_service_token: str = Field(default="change-this-internal-ai-token", alias="AI_INTERNAL_SERVICE_TOKEN")
    openai_compatible_api_key: str | None = Field(default=None, alias="OPENAI_COMPATIBLE_API_KEY")
    openai_compatible_base_url: str | None = Field(default=None, alias="OPENAI_COMPATIBLE_BASE_URL")
    openai_compatible_default_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_COMPATIBLE_DEFAULT_MODEL")
    pinecone_api_key: str | None = Field(default=None, alias="PINECONE_API_KEY")
    pinecone_index: str | None = Field(default=None, alias="PINECONE_INDEX")
    cors_origins: list[str] = Field(default=["http://localhost:3000"], alias="CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
