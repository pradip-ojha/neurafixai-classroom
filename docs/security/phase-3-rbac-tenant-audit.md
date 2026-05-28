# Phase 3 RBAC, Tenant Context, And Audit

Implemented:

- `roles`
- `permissions`
- `role_permissions`
- `user_roles`
- `user_permission_overrides`
- `audit_logs`
- Default permission seed list
- Institution owner bootstrap role
- Redis-backed permission cache with DB fallback
- JWT/session-derived tenant context
- Reusable FastAPI dependency: `require_permission("permission.code")`
- Current-user permission endpoint
- Permission catalog endpoint
- Role list endpoint
- Tenant-scoped audit log endpoint

Security rules:

- Protected endpoints derive `institution_id` from the access token and active session.
- Endpoints must not accept frontend-provided `institution_id` as authority.
- Permission checks run on the backend.
- Permission cache is an optimization only; PostgreSQL remains the source of truth.
- Audit logs are tenant-scoped and require `audit_logs.view`.

Deferred:

- Full role creation/update APIs
- User role assignment APIs
- Permission override APIs
- Redis-backed rate limiting
- PostgreSQL Row Level Security hardening

