from datetime import timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.security import utc_now
from app.models import RefreshToken, RefreshTokenStatus
from app.services.auth_service import AuthService


class FakeRepo:
    def __init__(self, token: RefreshToken) -> None:
        self.token = token
        self.revoked_family = False
        self.revoked_sessions = False
        self.committed = False
        self.added = []

    async def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken:
        return self.token

    async def revoke_refresh_family(self, **kwargs) -> None:
        self.revoked_family = True

    async def revoke_user_sessions(self, **kwargs) -> None:
        self.revoked_sessions = True

    def add(self, entity) -> None:
        self.added.append(entity)

    async def commit(self) -> None:
        self.committed = True


@pytest.mark.asyncio
async def test_refresh_token_reuse_revokes_family_and_sessions() -> None:
    existing = RefreshToken(
        id=uuid4(),
        institution_id=uuid4(),
        user_id=uuid4(),
        user_session_id=uuid4(),
        token_hash="stored-hash",
        family_id=uuid4(),
        status=RefreshTokenStatus.rotated,
        expires_at=utc_now() + timedelta(days=1),
    )
    repo = FakeRepo(existing)
    service = AuthService.__new__(AuthService)
    service.repo = repo
    service.settings = SimpleNamespace(refresh_token_days=30, access_token_minutes=15)

    with pytest.raises(HTTPException) as exc:
        await service.refresh(
            refresh_token="previous-raw-refresh-token",
            ip_address="127.0.0.1",
            user_agent="pytest",
        )

    assert exc.value.status_code == 401
    assert existing.status == RefreshTokenStatus.reused
    assert repo.revoked_family
    assert repo.revoked_sessions
    assert repo.committed
    assert repo.added[0].event_type == "refresh_token_reuse_detected"

