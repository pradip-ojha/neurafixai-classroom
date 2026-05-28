from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import get_current_tenant
from app.core.permissions import DEFAULT_PERMISSION_CODES
from app.core.security import create_access_token, utc_now
from app.models import User, UserSession, UserStatus
from app.services.permission_service import PermissionService


class FakeCache:
    def __init__(self, cached=None) -> None:
        self.cached = cached
        self.stored = None
        self.invalidated = None

    async def get_user_permissions(self, institution_id, user_id):
        return self.cached

    async def set_user_permissions(self, institution_id, user_id, permissions):
        self.stored = (institution_id, user_id, permissions)

    async def invalidate_user_permissions(self, institution_id, user_id):
        self.invalidated = (institution_id, user_id)


class FakeRepo:
    def __init__(self, permissions: set[str]) -> None:
        self.permissions = permissions
        self.resolve_called = False

    async def resolve_user_permissions(self, institution_id, user_id):
        self.resolve_called = True
        return self.permissions


class FakeDb:
    def __init__(self, user: User, session: UserSession) -> None:
        self.user = user
        self.session = session

    async def get(self, model, entity_id):
        if model is User:
            return self.user
        if model is UserSession:
            return self.session
        return None


def test_default_permission_catalog_contains_core_permissions() -> None:
    assert "roles.manage" in DEFAULT_PERMISSION_CODES
    assert "permissions.read" in DEFAULT_PERMISSION_CODES
    assert "audit_logs.view" in DEFAULT_PERMISSION_CODES
    assert "ai_tutor.use" in DEFAULT_PERMISSION_CODES


@pytest.mark.asyncio
async def test_permission_service_uses_cache_before_database() -> None:
    service = PermissionService.__new__(PermissionService)
    service.cache = FakeCache(cached={"students.read"})
    service.repo = FakeRepo(permissions={"roles.manage"})

    permissions = await service.get_user_permissions(uuid4(), uuid4())

    assert permissions == {"students.read"}
    assert service.repo.resolve_called is False


@pytest.mark.asyncio
async def test_permission_service_populates_cache_from_database() -> None:
    cache = FakeCache(cached=None)
    service = PermissionService.__new__(PermissionService)
    service.cache = cache
    service.repo = FakeRepo(permissions={"roles.manage", "permissions.read"})

    institution_id = uuid4()
    user_id = uuid4()
    permissions = await service.get_user_permissions(institution_id, user_id)

    assert permissions == {"roles.manage", "permissions.read"}
    assert service.repo.resolve_called is True
    assert cache.stored == (institution_id, user_id, permissions)


@pytest.mark.asyncio
async def test_require_permission_rejects_missing_permission() -> None:
    service = PermissionService.__new__(PermissionService)
    service.cache = FakeCache(cached={"students.read"})
    service.repo = FakeRepo(permissions=set())

    with pytest.raises(HTTPException) as exc:
        await service.require_permission(uuid4(), uuid4(), "roles.manage")

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_current_tenant_is_derived_from_access_token_and_active_session() -> None:
    institution_id = uuid4()
    user_id = uuid4()
    session_id = uuid4()
    token = create_access_token(
        user_id=user_id,
        institution_id=institution_id,
        session_id=session_id,
    )
    user = User(
        id=user_id,
        institution_id=institution_id,
        email="owner@example.com",
        password_hash="hash",
        status=UserStatus.active,
    )
    session = UserSession(
        id=session_id,
        institution_id=institution_id,
        user_id=user_id,
        session_token_id="session-token-id",
        expires_at=utc_now() + timedelta(days=1),
    )

    tenant = await get_current_tenant(
        credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials=token),
        db=FakeDb(user, session),
    )

    assert tenant.institution_id == institution_id
    assert tenant.user_id == user_id
    assert tenant.session_id == session_id
    assert tenant.user is user


@pytest.mark.asyncio
async def test_current_tenant_rejects_cross_tenant_session() -> None:
    institution_id = uuid4()
    token = create_access_token(
        user_id=uuid4(),
        institution_id=institution_id,
        session_id=uuid4(),
    )
    user = User(
        id=uuid4(),
        institution_id=uuid4(),
        email="owner@example.com",
        password_hash="hash",
        status=UserStatus.active,
    )
    session = UserSession(
        id=uuid4(),
        institution_id=institution_id,
        user_id=user.id,
        session_token_id="session-token-id",
        expires_at=utc_now() + timedelta(days=1),
    )

    with pytest.raises(HTTPException) as exc:
        await get_current_tenant(
            credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials=token),
            db=FakeDb(user, session),
        )

    assert exc.value.status_code == 401
