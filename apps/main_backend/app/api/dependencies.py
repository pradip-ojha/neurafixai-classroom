from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token, utc_now
from app.core.tenant import TenantContext
from app.db.session import get_db
from app.models import User, UserSession, UserStatus
from app.services.permission_service import PermissionService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_tenant(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> TenantContext:
    if not credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
        institution_id = UUID(payload["institution_id"])
        session_id = UUID(payload["session_id"])
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid access token") from None

    user = await db.get(User, user_id)
    session = await db.get(UserSession, session_id)
    now = utc_now()

    if (
        not user
        or user.institution_id != institution_id
        or user.status != UserStatus.active
        or user.deleted_at is not None
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid access token")

    if (
        not session
        or session.user_id != user.id
        or session.institution_id != institution_id
        or session.revoked_at is not None
        or session.expires_at <= now
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session is no longer active")

    return TenantContext(
        institution_id=institution_id,
        user_id=user.id,
        session_id=session.id,
        user=user,
    )


def require_permission(permission: str):
    async def dependency(
        tenant: TenantContext = Depends(get_current_tenant),
        db: AsyncSession = Depends(get_db),
    ) -> TenantContext:
        await PermissionService(db).require_permission(
            tenant.institution_id,
            tenant.user_id,
            permission,
        )
        return tenant

    return dependency

