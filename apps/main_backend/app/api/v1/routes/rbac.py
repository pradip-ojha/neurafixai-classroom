from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_tenant, require_permission
from app.core.tenant import TenantContext
from app.db.session import get_db
from app.models import AuditLog
from app.repositories.permission_repository import PermissionRepository
from app.schemas.common import ApiResponse
from app.schemas.rbac import AuditLogData, CurrentPermissionsData, PermissionData, RoleData
from app.services.permission_service import PermissionService

router = APIRouter(tags=["rbac"])


@router.get("/me/permissions", response_model=ApiResponse[CurrentPermissionsData])
async def my_permissions(
    request: Request,
    tenant: TenantContext = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CurrentPermissionsData]:
    permissions = await PermissionService(db).get_user_permissions(
        tenant.institution_id,
        tenant.user_id,
    )
    return ApiResponse(
        data=CurrentPermissionsData(
            institution_id=tenant.institution_id,
            user_id=tenant.user_id,
            permissions=sorted(permissions),
        ),
        message="Permissions loaded.",
        request_id=request.state.request_id,
    )


@router.get(
    "/permissions",
    response_model=ApiResponse[list[PermissionData]],
)
async def list_permissions(
    request: Request,
    tenant: TenantContext = Depends(require_permission("permissions.read")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[PermissionData]]:
    permissions = await PermissionRepository(db).list_permissions()
    return ApiResponse(
        data=[PermissionData.model_validate(permission) for permission in permissions],
        message="Permissions loaded.",
        request_id=request.state.request_id,
    )


@router.get(
    "/roles",
    response_model=ApiResponse[list[RoleData]],
)
async def list_roles(
    request: Request,
    tenant: TenantContext = Depends(require_permission("roles.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[RoleData]]:
    roles = await PermissionRepository(db).list_roles(tenant.institution_id)
    return ApiResponse(
        data=[RoleData.model_validate(role) for role in roles],
        message="Roles loaded.",
        request_id=request.state.request_id,
    )


@router.get(
    "/audit-logs",
    response_model=ApiResponse[list[AuditLogData]],
)
async def list_audit_logs(
    request: Request,
    tenant: TenantContext = Depends(require_permission("audit_logs.view")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
) -> ApiResponse[list[AuditLogData]]:
    capped_limit = max(1, min(limit, 100))
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.institution_id == tenant.institution_id)
        .order_by(AuditLog.created_at.desc())
        .limit(capped_limit)
    )
    logs = list(result.scalars().all())
    return ApiResponse(
        data=[AuditLogData.model_validate(log) for log in logs],
        message="Audit logs loaded.",
        request_id=request.state.request_id,
    )

