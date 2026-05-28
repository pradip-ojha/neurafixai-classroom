# Phase 2 Authentication

Implemented:

- Institution owner registration
- Email verification token storage
- Password reset token storage
- Argon2 password hashing
- JWT access tokens
- Hashed refresh tokens
- Refresh token rotation
- Refresh token family invalidation on reuse
- User sessions
- Login attempts
- Account lockout fields
- Security events
- Standard API error envelope

Important security rules:

- Raw refresh tokens are never stored.
- Raw reset and email verification tokens are never stored.
- A reused rotated/revoked refresh token revokes the full token family and user sessions.
- Login responses do not reveal whether an email exists.
- Development-only email/password reset tokens are included only outside production.

Deferred:

- Email delivery worker integration
- OAuth
- 2FA
- Redis-backed rate limiter dependency
