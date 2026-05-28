from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_permission
from app.core.tenant import TenantContext
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.files import FileObjectData, FileUploadUrlRequest, SignedFileUrlData
from app.services.files_service import FilesService

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload-url", response_model=ApiResponse[SignedFileUrlData], status_code=201)
async def create_upload_url(
    payload: FileUploadUrlRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("files.upload")),
    db: AsyncSession = Depends(get_db),
):
    file_object, url, expires = await FilesService(db).create_upload_url(
        tenant.institution_id,
        tenant.user_id,
        **payload.model_dump(),
    )
    return ApiResponse(
        data=SignedFileUrlData(
            file=FileObjectData.model_validate(file_object),
            url=url,
            expires_in_seconds=expires,
        ),
        message="Upload URL created.",
        request_id=request.state.request_id,
    )


@router.get("/{file_id}/download-url", response_model=ApiResponse[SignedFileUrlData])
async def create_download_url(
    file_id: UUID,
    request: Request,
    tenant: TenantContext = Depends(require_permission("files.download")),
    db: AsyncSession = Depends(get_db),
):
    file_object, url, expires = await FilesService(db).create_download_url(
        tenant.institution_id,
        tenant.user_id,
        file_id,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    return ApiResponse(
        data=SignedFileUrlData(
            file=FileObjectData.model_validate(file_object),
            url=url,
            expires_in_seconds=expires,
        ),
        message="Download URL created.",
        request_id=request.state.request_id,
    )


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else None
