from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Institution,
    LoginAttempt,
    RefreshToken,
    RefreshTokenStatus,
    User,
    UserProfile,
    UserSession,
    UserStatus,
)


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_institution_by_slug(self, slug: str) -> Institution | None:
        result = await self.session.execute(select(Institution).where(Institution.slug == slug))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, institution_id: uuid.UUID, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(
                User.institution_id == institution_id,
                User.email == email,
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def count_failed_login_attempts(
        self,
        *,
        email: str,
        since: datetime,
        ip_address: str | None,
    ) -> int:
        statement: Select = select(func.count()).select_from(LoginAttempt).where(
            LoginAttempt.email == email,
            LoginAttempt.success.is_(False),
            LoginAttempt.created_at >= since,
        )
        if ip_address:
            statement = statement.where(LoginAttempt.ip_address == ip_address)

        result = await self.session.execute(statement)
        return int(result.scalar_one())

    def add(self, entity: object) -> None:
        self.session.add(entity)

    async def flush(self) -> None:
        await self.session.flush()

    async def revoke_refresh_family(
        self,
        *,
        family_id: uuid.UUID,
        revoked_at: datetime,
        status: RefreshTokenStatus = RefreshTokenStatus.revoked,
    ) -> None:
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == family_id)
            .values(status=status, revoked_at=revoked_at)
        )

    async def revoke_user_sessions(
        self,
        *,
        user_id: uuid.UUID,
        revoked_at: datetime,
        reason: str,
    ) -> None:
        await self.session.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id, UserSession.revoked_at.is_(None))
            .values(revoked_at=revoked_at, revoked_reason=reason)
        )

    async def create_institution_with_owner(
        self,
        *,
        institution_name: str,
        institution_slug: str,
        full_name: str,
        email: str,
        password_hash: str,
    ) -> tuple[Institution, User]:
        institution = Institution(name=institution_name, slug=institution_slug)
        self.session.add(institution)
        await self.session.flush()

        user = User(
            institution_id=institution.id,
            email=email,
            password_hash=password_hash,
            status=UserStatus.pending,
        )
        self.session.add(user)
        await self.session.flush()

        self.session.add(
            UserProfile(
                institution_id=institution.id,
                user_id=user.id,
                full_name=full_name,
            )
        )
        return institution, user

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
