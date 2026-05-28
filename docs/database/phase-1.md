# Phase 1 Database

Phase 1 only wires PostgreSQL and Alembic.

The first business migration should be created in Phase 2 for authentication tables:

- institutions
- users
- user_profiles
- user_sessions
- refresh_tokens
- login_attempts
- password_reset_tokens
- email_verification_tokens
- security_events

All tenant-owned tables introduced from Phase 3 onward must include `institution_id` and tenant indexes.

