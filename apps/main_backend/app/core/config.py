from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = Field(default="local", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field(default="amqp://guest:guest@rabbitmq:5672//", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://redis:6379/1", alias="CELERY_RESULT_BACKEND")
    jwt_secret_key: str = Field(
        default="change-this-before-production-32-byte-minimum",
        alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_minutes: int = Field(default=15, alias="ACCESS_TOKEN_MINUTES")
    refresh_token_days: int = Field(default=30, alias="REFRESH_TOKEN_DAYS")
    email_verification_hours: int = Field(default=24, alias="EMAIL_VERIFICATION_HOURS")
    password_reset_minutes: int = Field(default=30, alias="PASSWORD_RESET_MINUTES")
    login_lockout_minutes: int = Field(default=15, alias="LOGIN_LOCKOUT_MINUTES")
    max_failed_login_attempts: int = Field(default=5, alias="MAX_FAILED_LOGIN_ATTEMPTS")
    ai_service_internal_url: str = Field(default="http://ai_service:8001", alias="AI_SERVICE_INTERNAL_URL")
    ai_internal_service_token: str = Field(default="change-this-internal-ai-token", alias="AI_INTERNAL_SERVICE_TOKEN")
    object_storage_bucket: str = Field(default="neurafix-school-os-local", alias="OBJECT_STORAGE_BUCKET")
    object_storage_public_base_url: str = Field(
        default="http://localhost:9000/neurafix-school-os-local",
        alias="OBJECT_STORAGE_PUBLIC_BASE_URL",
    )
    signed_url_secret: str = Field(default="change-this-signed-url-secret", alias="SIGNED_URL_SECRET")
    signed_url_expiry_seconds: int = Field(default=900, alias="SIGNED_URL_EXPIRY_SECONDS")
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
