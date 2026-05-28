from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_permission
from app.core.tenant import TenantContext
from app.db.session import get_db
from app.repositories.content_repository import ContentRepository
from app.schemas.common import ApiResponse
from app.schemas.content import (
    ContentApprovalRequest,
    ContentItemCreateRequest,
    ContentItemData,
    ContentVersionCreateRequest,
)
from app.services.content_service import ContentService

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/items", response_model=ApiResponse[list[ContentItemData]])
async def list_content_items(
    request: Request,
    tenant: TenantContext = Depends(require_permission("content.read")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    rows = await ContentRepository(db).list_items(tenant.institution_id, _limit(limit), _offset(offset))
    return ApiResponse(
        data=[ContentItemData.model_validate(row) for row in rows],
        message="Content items loaded.",
        request_id=request.state.request_id,
    )


@router.post("/items", response_model=ApiResponse[ContentItemData], status_code=201)
async def create_content_item(
    payload: ContentItemCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("content.upload")),
    db: AsyncSession = Depends(get_db),
):
    item = await ContentService(db).create_item(
        tenant.institution_id,
        tenant.user_id,
        **payload.model_dump(),
    )
    return ApiResponse(
        data=ContentItemData.model_validate(item),
        message="Content item created.",
        request_id=request.state.request_id,
    )


@router.post("/items/{content_item_id}/versions", response_model=ApiResponse[ContentItemData], status_code=201)
async def create_content_version(
    content_item_id: UUID,
    payload: ContentVersionCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("content.update")),
    db: AsyncSession = Depends(get_db),
):
    item = await ContentService(db).create_version(
        tenant.institution_id,
        tenant.user_id,
        content_item_id,
        **payload.model_dump(),
    )
    return ApiResponse(
        data=ContentItemData.model_validate(item),
        message="Content version created.",
        request_id=request.state.request_id,
    )


@router.post("/items/{content_item_id}/approval", response_model=ApiResponse[ContentItemData])
async def review_content_item(
    content_item_id: UUID,
    payload: ContentApprovalRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("content.approve")),
    db: AsyncSession = Depends(get_db),
):
    item = await ContentService(db).review_item(
        tenant.institution_id,
        tenant.user_id,
        content_item_id,
        status_value=payload.status,
        comment=payload.comment,
    )
    return ApiResponse(
        data=ContentItemData.model_validate(item),
        message="Content reviewed.",
        request_id=request.state.request_id,
    )


def _limit(value: int) -> int:
    return max(1, min(value, 100))


def _offset(value: int) -> int:
    return max(0, value)
