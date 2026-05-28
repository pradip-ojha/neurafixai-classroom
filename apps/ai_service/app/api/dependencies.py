from fastapi import Header, HTTPException, status

from app.core.config import get_settings


async def require_internal_service(
    token: str | None = Header(default=None, alias="X-Internal-Service-Token"),
) -> None:
    if token != get_settings().ai_internal_service_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid internal service token")
