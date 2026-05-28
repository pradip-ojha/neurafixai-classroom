from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    generate_opaque_token,
    hash_password,
    hash_token,
    utc_now,
    verify_password,
)
from app.models import (
    EmailVerificationToken,
    LoginAttempt,
    PasswordResetToken,
    RefreshToken,
    RefreshTokenStatus,
    SecurityEvent,
    User,
    UserSession,
    UserStatus,
)
from app.repositories.auth_repository import AuthRepository
from app.services.permission_service import PermissionService


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AuthRepository(session)
        self.settings = get_settings()

    async def register_institution(
        self,
        *,
        institution_name: str,
        institution_slug: str,
        full_name: str,
        email: str,
        password: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> dict:
        normalized_email = normalize_email(email)
        normalized_slug = normalize_slug(institution_slug)

        if await self.repo.get_institution_by_slug(normalized_slug):
            raise HTTPException(status.HTTP_409_CONFLICT, "Institution slug already exists")

        institution, user = await self.repo.create_institution_with_owner(
            institution_name=institution_name.strip(),
            institution_slug=normalized_slug,
            full_name=full_name.strip(),
            email=normalized_email,
            password_hash=hash_password(password),
        )

        verification_token = await self._create_email_verification_token(user)
        self._security_event(
            event_type="institution_owner_registered",
            severity="info",
            institution_id=institution.id,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await PermissionService(self.repo.session).bootstrap_institution_owner(
            institution_id=institution.id,
            user_id=user.id,
        )

        await self.repo.commit()

        payload = {
            "institution_id": institution.id,
            "user_id": user.id,
            "email": user.email,
            "status": user.status.value,
        }
        if self.settings.environment != "production":
            payload["dev_email_verification_token"] = verification_token
        return payload

    async def verify_email(self, *, token: str) -> None:
        token_hash = hash_token(token)
        now = utc_now()
        result = await self.repo.session.execute(
            select_email_verification_token(token_hash)
        )
        token_row = result.scalar_one_or_none()
        if not token_row or token_row.used_at or token_row.expires_at <= now:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired verification token")

        user = await self.repo.session.get(User, token_row.user_id)
        if not user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid verification token")

        token_row.used_at = now
        user.email_verified_at = now
        user.status = UserStatus.active
        self._security_event(
            event_type="email_verified",
            severity="info",
            institution_id=user.institution_id,
            user_id=user.id,
        )
        await self.repo.commit()

    async def login(
        self,
        *,
        institution_slug: str,
        email: str,
        password: str,
        ip_address: str | None,
        user_agent: str | None,
        device_name: str | None,
    ) -> TokenPair:
        normalized_email = normalize_email(email)
        institution = await self.repo.get_institution_by_slug(normalize_slug(institution_slug))
        if not institution:
            await self._record_login_attempt(None, normalized_email, ip_address, user_agent, False, "not_found")
            raise invalid_credentials()

        locked_since = utc_now() - timedelta(minutes=self.settings.login_lockout_minutes)
        recent_failures = await self.repo.count_failed_login_attempts(
            email=normalized_email,
            since=locked_since,
            ip_address=ip_address,
        )
        if recent_failures >= self.settings.max_failed_login_attempts:
            self._security_event(
                event_type="login_throttled",
                severity="warning",
                institution_id=institution.id,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={"email": normalized_email},
            )
            await self.repo.commit()
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many login attempts")

        user = await self.repo.get_user_by_email(institution.id, normalized_email)
        if not user or not verify_password(password, user.password_hash):
            await self._record_login_attempt(
                institution.id,
                normalized_email,
                ip_address,
                user_agent,
                False,
                "invalid_credentials",
            )
            if user:
                user.failed_login_count += 1
                if user.failed_login_count >= self.settings.max_failed_login_attempts:
                    user.status = UserStatus.locked
                    user.locked_until = utc_now() + timedelta(minutes=self.settings.login_lockout_minutes)
            await self.repo.commit()
            raise invalid_credentials()

        if user.status == UserStatus.pending:
            await self._record_login_attempt(
                institution.id,
                normalized_email,
                ip_address,
                user_agent,
                False,
                "email_not_verified",
            )
            await self.repo.commit()
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Email verification required")

        if user.status in {UserStatus.disabled, UserStatus.locked}:
            await self._record_login_attempt(
                institution.id,
                normalized_email,
                ip_address,
                user_agent,
                False,
                "account_unavailable",
            )
            await self.repo.commit()
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is not available")

        user.failed_login_count = 0
        user.locked_until = None
        user.last_login_at = utc_now()
        await self._record_login_attempt(
            institution.id,
            normalized_email,
            ip_address,
            user_agent,
            True,
            None,
        )
        pair = await self._create_session_and_tokens(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=device_name,
        )
        self._security_event(
            event_type="login_success",
            severity="info",
            institution_id=user.institution_id,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.repo.commit()
        return pair

    async def refresh(self, *, refresh_token: str, ip_address: str | None, user_agent: str | None) -> TokenPair:
        now = utc_now()
        token_hash = hash_token(refresh_token)
        existing = await self.repo.get_refresh_token_by_hash(token_hash)
        if not existing:
            raise invalid_refresh()

        if existing.status != RefreshTokenStatus.active or existing.revoked_at or existing.expires_at <= now:
            existing.status = RefreshTokenStatus.reused
            await self.repo.revoke_refresh_family(
                family_id=existing.family_id,
                revoked_at=now,
                status=RefreshTokenStatus.reused,
            )
            await self.repo.revoke_user_sessions(
                user_id=existing.user_id,
                revoked_at=now,
                reason="refresh_token_reuse_detected",
            )
            self._security_event(
                event_type="refresh_token_reuse_detected",
                severity="critical",
                institution_id=existing.institution_id,
                user_id=existing.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            await self.repo.commit()
            raise invalid_refresh()

        session = await self.repo.session.get(UserSession, existing.user_session_id)
        user = await self.repo.session.get(User, existing.user_id)
        if not session or not user or session.revoked_at or session.expires_at <= now:
            raise invalid_refresh()

        raw_token = generate_opaque_token()
        new_token = RefreshToken(
            institution_id=existing.institution_id,
            user_id=existing.user_id,
            user_session_id=existing.user_session_id,
            token_hash=hash_token(raw_token),
            family_id=existing.family_id,
            parent_token_id=existing.id,
            expires_at=now + timedelta(days=self.settings.refresh_token_days),
        )
        self.repo.add(new_token)
        await self.repo.flush()

        existing.status = RefreshTokenStatus.rotated
        existing.rotated_at = now
        existing.replaced_by_token_id = new_token.id
        session.last_seen_at = now

        access_token = create_access_token(
            user_id=user.id,
            institution_id=user.institution_id,
            session_id=session.id,
        )
        await self.repo.commit()
        return TokenPair(
            access_token=access_token,
            refresh_token=raw_token,
            expires_in=self.settings.access_token_minutes * 60,
        )

    async def logout(self, *, refresh_token: str) -> None:
        existing = await self.repo.get_refresh_token_by_hash(hash_token(refresh_token))
        if not existing:
            return

        now = utc_now()
        existing.status = RefreshTokenStatus.revoked
        existing.revoked_at = now
        session = await self.repo.session.get(UserSession, existing.user_session_id)
        if session:
            session.revoked_at = now
            session.revoked_reason = "logout"
        await self.repo.commit()

    async def logout_all(self, *, refresh_token: str) -> None:
        existing = await self.repo.get_refresh_token_by_hash(hash_token(refresh_token))
        if not existing:
            return

        now = utc_now()
        await self.repo.revoke_user_sessions(
            user_id=existing.user_id,
            revoked_at=now,
            reason="logout_all",
        )
        await self.repo.revoke_refresh_family(family_id=existing.family_id, revoked_at=now)
        await self.repo.commit()

    async def request_password_reset(
        self,
        *,
        institution_slug: str,
        email: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> dict:
        institution = await self.repo.get_institution_by_slug(normalize_slug(institution_slug))
        normalized_email = normalize_email(email)
        dev_token = None

        if institution:
            user = await self.repo.get_user_by_email(institution.id, normalized_email)
            if user:
                dev_token = await self._create_password_reset_token(user)
                self._security_event(
                    event_type="password_reset_requested",
                    severity="info",
                    institution_id=user.institution_id,
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )

        await self.repo.commit()
        response = {"message": "If the account exists, a reset link will be sent."}
        if dev_token and self.settings.environment != "production":
            response["dev_password_reset_token"] = dev_token
        return response

    async def confirm_password_reset(self, *, token: str, new_password: str) -> None:
        token_hash = hash_token(token)
        now = utc_now()
        result = await self.repo.session.execute(select_password_reset_token(token_hash))
        token_row = result.scalar_one_or_none()
        if not token_row or token_row.used_at or token_row.expires_at <= now:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired reset token")

        user = await self.repo.session.get(User, token_row.user_id)
        if not user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid reset token")

        user.password_hash = hash_password(new_password)
        user.failed_login_count = 0
        user.locked_until = None
        if user.status == UserStatus.locked:
            user.status = UserStatus.active
        token_row.used_at = now
        await self.repo.revoke_user_sessions(
            user_id=user.id,
            revoked_at=now,
            reason="password_reset",
        )
        self._security_event(
            event_type="password_reset_completed",
            severity="warning",
            institution_id=user.institution_id,
            user_id=user.id,
        )
        await self.repo.commit()

    async def _create_session_and_tokens(
        self,
        *,
        user: User,
        ip_address: str | None,
        user_agent: str | None,
        device_name: str | None,
    ) -> TokenPair:
        now = utc_now()
        session = UserSession(
            institution_id=user.institution_id,
            user_id=user.id,
            session_token_id=str(uuid.uuid4()),
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=device_name,
            last_seen_at=now,
            expires_at=now + timedelta(days=self.settings.refresh_token_days),
        )
        self.repo.add(session)
        await self.repo.flush()

        raw_refresh = generate_opaque_token()
        refresh = RefreshToken(
            institution_id=user.institution_id,
            user_id=user.id,
            user_session_id=session.id,
            token_hash=hash_token(raw_refresh),
            family_id=uuid.uuid4(),
            expires_at=now + timedelta(days=self.settings.refresh_token_days),
        )
        self.repo.add(refresh)

        access_token = create_access_token(
            user_id=user.id,
            institution_id=user.institution_id,
            session_id=session.id,
        )
        return TokenPair(
            access_token=access_token,
            refresh_token=raw_refresh,
            expires_in=self.settings.access_token_minutes * 60,
        )

    async def _create_email_verification_token(self, user: User) -> str:
        raw_token = generate_opaque_token()
        self.repo.add(
            EmailVerificationToken(
                institution_id=user.institution_id,
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=utc_now() + timedelta(hours=self.settings.email_verification_hours),
            )
        )
        return raw_token

    async def _create_password_reset_token(self, user: User) -> str:
        raw_token = generate_opaque_token()
        self.repo.add(
            PasswordResetToken(
                institution_id=user.institution_id,
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=utc_now() + timedelta(minutes=self.settings.password_reset_minutes),
            )
        )
        return raw_token

    async def _record_login_attempt(
        self,
        institution_id: uuid.UUID | None,
        email: str,
        ip_address: str | None,
        user_agent: str | None,
        success: bool,
        failure_reason: str | None,
    ) -> None:
        self.repo.add(
            LoginAttempt(
                institution_id=institution_id,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                failure_reason=failure_reason,
            )
        )

    def _security_event(
        self,
        *,
        event_type: str,
        severity: str,
        institution_id: uuid.UUID | None,
        user_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        self.repo.add(
            SecurityEvent(
                institution_id=institution_id,
                user_id=user_id,
                event_type=event_type,
                severity=severity,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata_json=metadata,
            )
        )


def normalize_email(email: str) -> str:
    return email.strip().lower()


def normalize_slug(slug: str) -> str:
    return slug.strip().lower()


def invalid_credentials() -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")


def invalid_refresh() -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")


def select_email_verification_token(token_hash: str):
    from sqlalchemy import select

    return select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash)


def select_password_reset_token(token_hash: str):
    from sqlalchemy import select

    return select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
