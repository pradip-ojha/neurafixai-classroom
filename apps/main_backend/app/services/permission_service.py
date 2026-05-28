from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.permission_repository import PermissionRepository
from app.services.permission_cache import PermissionCache


class PermissionService:
    def __init__(self, session: AsyncSession, cache: PermissionCache | None = None) -> None:
        self.repo = PermissionRepository(session)
        self.cache = cache or PermissionCache()

    async def bootstrap_institution_owner(self, institution_id: UUID, user_id: UUID) -> None:
        role = await self.repo.ensure_institution_owner_role(institution_id)
        await self.repo.assign_all_permissions_to_role(role)
        await self.repo.assign_role_to_user(institution_id, user_id, role.id)
        await self.cache.invalidate_user_permissions(institution_id, user_id)

    async def get_user_permissions(self, institution_id: UUID, user_id: UUID) -> set[str]:
        cached = await self.cache.get_user_permissions(institution_id, user_id)
        if cached is not None:
            return cached

        permissions = await self.repo.resolve_user_permissions(institution_id, user_id)
        await self.cache.set_user_permissions(institution_id, user_id, permissions)
        return permissions

    async def require_permission(self, institution_id: UUID, user_id: UUID, permission: str) -> None:
        permissions = await self.get_user_permissions(institution_id, user_id)
        if permission not in permissions:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission.")

