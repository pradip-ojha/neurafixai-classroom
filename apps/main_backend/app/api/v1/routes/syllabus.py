from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_permission
from app.core.tenant import TenantContext
from app.db.session import get_db
from app.repositories.syllabus_repository import SyllabusRepository
from app.schemas.common import ApiResponse
from app.schemas.syllabus import (
    LearningObjectiveCreateRequest,
    LearningObjectiveData,
    SyllabusChapterCreateRequest,
    SyllabusChapterData,
    SyllabusSubtopicCreateRequest,
    SyllabusSubtopicData,
    SyllabusTopicCreateRequest,
    SyllabusTopicData,
)
from app.services.syllabus_service import SyllabusService

router = APIRouter(prefix="/syllabus", tags=["syllabus"])


@router.get("/chapters", response_model=ApiResponse[list[SyllabusChapterData]])
async def list_chapters(
    request: Request,
    tenant: TenantContext = Depends(require_permission("syllabus.manage")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    rows = await SyllabusRepository(db).list_chapters(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [SyllabusChapterData.model_validate(row) for row in rows], "Chapters loaded.")


@router.post("/chapters", response_model=ApiResponse[SyllabusChapterData], status_code=201)
async def create_chapter(
    payload: SyllabusChapterCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("syllabus.manage")),
    db: AsyncSession = Depends(get_db),
):
    row = await SyllabusService(db).create_chapter(tenant.institution_id, **payload.model_dump())
    return _response(request, SyllabusChapterData.model_validate(row), "Chapter created.")


@router.get("/topics", response_model=ApiResponse[list[SyllabusTopicData]])
async def list_topics(
    request: Request,
    tenant: TenantContext = Depends(require_permission("syllabus.manage")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    rows = await SyllabusRepository(db).list_topics(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [SyllabusTopicData.model_validate(row) for row in rows], "Topics loaded.")


@router.post("/topics", response_model=ApiResponse[SyllabusTopicData], status_code=201)
async def create_topic(
    payload: SyllabusTopicCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("syllabus.manage")),
    db: AsyncSession = Depends(get_db),
):
    row = await SyllabusService(db).create_topic(tenant.institution_id, **payload.model_dump())
    return _response(request, SyllabusTopicData.model_validate(row), "Topic created.")


@router.get("/subtopics", response_model=ApiResponse[list[SyllabusSubtopicData]])
async def list_subtopics(
    request: Request,
    tenant: TenantContext = Depends(require_permission("syllabus.manage")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    rows = await SyllabusRepository(db).list_subtopics(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [SyllabusSubtopicData.model_validate(row) for row in rows], "Subtopics loaded.")


@router.post("/subtopics", response_model=ApiResponse[SyllabusSubtopicData], status_code=201)
async def create_subtopic(
    payload: SyllabusSubtopicCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("syllabus.manage")),
    db: AsyncSession = Depends(get_db),
):
    row = await SyllabusService(db).create_subtopic(tenant.institution_id, **payload.model_dump())
    return _response(request, SyllabusSubtopicData.model_validate(row), "Subtopic created.")


@router.get("/objectives", response_model=ApiResponse[list[LearningObjectiveData]])
async def list_objectives(
    request: Request,
    tenant: TenantContext = Depends(require_permission("syllabus.manage")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    rows = await SyllabusRepository(db).list_objectives(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [LearningObjectiveData.model_validate(row) for row in rows], "Objectives loaded.")


@router.post("/objectives", response_model=ApiResponse[LearningObjectiveData], status_code=201)
async def create_objective(
    payload: LearningObjectiveCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("syllabus.manage")),
    db: AsyncSession = Depends(get_db),
):
    row = await SyllabusService(db).create_objective(tenant.institution_id, **payload.model_dump())
    return _response(request, LearningObjectiveData.model_validate(row), "Objective created.")


def _response(request: Request, data, message: str):
    return ApiResponse(data=data, message=message, request_id=request.state.request_id)


def _limit(value: int) -> int:
    return max(1, min(value, 100))


def _offset(value: int) -> int:
    return max(0, value)
