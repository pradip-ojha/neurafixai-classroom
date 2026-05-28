from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_permission
from app.core.tenant import TenantContext
from app.db.session import get_db
from app.models import BackgroundJobStatus
from app.repositories.jobs_repository import JobsRepository
from app.schemas.common import ApiResponse
from app.schemas.jobs import BackgroundJobData, JobCancelRequest, JobDetailData, JobEventData
from app.services.jobs_service import JobsService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=ApiResponse[list[BackgroundJobData]])
async def list_jobs(
    request: Request,
    tenant: TenantContext = Depends(require_permission("jobs.read")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
    status: BackgroundJobStatus | None = None,
) -> ApiResponse[list[BackgroundJobData]]:
    rows = await JobsRepository(db).list_jobs(tenant.institution_id, _limit(limit), _offset(offset), status)
    return ApiResponse(
        data=[BackgroundJobData.model_validate(row) for row in rows],
        message="Jobs loaded.",
        request_id=request.state.request_id,
    )


@router.get("/{job_id}", response_model=ApiResponse[JobDetailData])
async def get_job(
    job_id: UUID,
    request: Request,
    tenant: TenantContext = Depends(require_permission("jobs.read")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[JobDetailData]:
    job, events = await JobsService(db).get_detail(tenant.institution_id, job_id)
    return ApiResponse(
        data=JobDetailData(
            job=BackgroundJobData.model_validate(job),
            events=[JobEventData.model_validate(event) for event in events],
        ),
        message="Job loaded.",
        request_id=request.state.request_id,
    )


@router.post("/{job_id}/cancel", response_model=ApiResponse[BackgroundJobData])
async def cancel_job(
    job_id: UUID,
    payload: JobCancelRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("jobs.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[BackgroundJobData]:
    job = await JobsService(db).cancel_job(tenant.institution_id, job_id, reason=payload.reason)
    return ApiResponse(
        data=BackgroundJobData.model_validate(job),
        message="Job cancelled.",
        request_id=request.state.request_id,
    )


def _limit(value: int) -> int:
    return max(1, min(value, 100))


def _offset(value: int) -> int:
    return max(0, value)
