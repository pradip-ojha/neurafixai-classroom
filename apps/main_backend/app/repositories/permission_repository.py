from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import DEFAULT_PERMISSIONS, INSTITUTION_OWNER_ROLE_SLUG
from app.models import (
    Permission,
    PermissionOverrideEffect,
    Role,
    RolePermission,
    UserPermissionOverride,
    UserRole,
)


class PermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ensure_default_permissions(self) -> dict[str, Permission]:
        existing = await self.session.execute(select(Permission))
        by_code = {permission.code: permission for permission in existing.scalars().all()}

        for seed in DEFAULT_PERMISSIONS:
            if seed.code not in by_code:
                permission = Permission(
                    id=seed.id,
                    code=seed.code,
                    category=seed.category,
                    description=seed.description,
                )
                self.session.add(permission)
                by_code[seed.code] = permission

        await self.session.flush()
        return by_code

    async def ensure_institution_owner_role(self, institution_id: UUID) -> Role:
        result = await self.session.execute(
            select(Role).where(
                Role.institution_id == institution_id,
                Role.slug == INSTITUTION_OWNER_ROLE_SLUG,
                Role.deleted_at.is_(None),
            )
        )
        role = result.scalar_one_or_none()
        if role:
            return role

        role = Role(
            institution_id=institution_id,
            name="Institution Owner",
            slug=INSTITUTION_OWNER_ROLE_SLUG,
            description="Full administrative role for the owning institution.",
            is_system=True,
        )
        self.session.add(role)
        await self.session.flush()
        return role

    async def assign_all_permissions_to_role(self, role: Role) -> None:
        permissions = await self.ensure_default_permissions()
        existing = await self.session.execute(
            select(RolePermission.permission_id).where(RolePermission.role_id == role.id)
        )
        existing_ids = set(existing.scalars().all())
        for permission in permissions.values():
            if permission.id not in existing_ids:
                self.session.add(
                    RolePermission(
                        institution_id=role.institution_id,
                        role_id=role.id,
                        permission_id=permission.id,
                    )
                )
        await self.session.flush()

    async def assign_role_to_user(self, institution_id: UUID, user_id: UUID, role_id: UUID) -> None:
        result = await self.session.execute(
            select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        if result.scalar_one_or_none():
            return

        self.session.add(UserRole(institution_id=institution_id, user_id=user_id, role_id=role_id))
        await self.session.flush()

    async def resolve_user_permissions(self, institution_id: UUID, user_id: UUID) -> set[str]:
        role_permissions = await self.session.execute(
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.institution_id == institution_id,
                UserRole.user_id == user_id,
                Role.deleted_at.is_(None),
            )
        )
        permissions = set(role_permissions.scalars().all())

        overrides = await self.session.execute(
            select(Permission.code, UserPermissionOverride.effect)
            .join(Permission, Permission.id == UserPermissionOverride.permission_id)
            .where(
                UserPermissionOverride.institution_id == institution_id,
                UserPermissionOverride.user_id == user_id,
            )
        )
        for code, effect in overrides.all():
            if effect == PermissionOverrideEffect.allow:
                permissions.add(code)
            else:
                permissions.discard(code)

        return permissions

    async def list_permissions(self) -> list[Permission]:
        result = await self.session.execute(select(Permission).order_by(Permission.category, Permission.code))
        return list(result.scalars().all())

    async def list_roles(self, institution_id: UUID) -> list[Role]:
        result = await self.session.execute(
            select(Role)
            .where(Role.institution_id == institution_id, Role.deleted_at.is_(None))
            .order_by(Role.name)
        )
        return list(result.scalars().all())

