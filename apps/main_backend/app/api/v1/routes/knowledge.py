from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_permission
from app.core.tenant import TenantContext
from app.db.session import get_db
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.common import ApiResponse
from app.schemas.jobs import BackgroundJobData
from app.schemas.knowledge import (
    KnowledgeBaseCreateRequest,
    KnowledgeBaseData,
    KnowledgeChunkData,
    KnowledgeDocumentCreateRequest,
    KnowledgeDocumentData,
    KnowledgeDocumentIngestData,
    RetrievalSearchData,
    RetrievalSearchRequest,
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


@router.get("/bases", response_model=ApiResponse[list[KnowledgeBaseData]])
async def list_bases(
    request: Request,
    tenant: TenantContext = Depends(require_permission("knowledge.read")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    rows = await KnowledgeRepository(db).list_bases(tenant.institution_id, _limit(limit), _offset(offset))
    return ApiResponse(
        data=[KnowledgeBaseData.model_validate(row) for row in rows],
        message="Knowledge bases loaded.",
        request_id=request.state.request_id,
    )


@router.post("/bases", response_model=ApiResponse[KnowledgeBaseData], status_code=201)
async def create_base(
    payload: KnowledgeBaseCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("knowledge.manage")),
    db: AsyncSession = Depends(get_db),
):
    row = await KnowledgeService(db).create_base(tenant.institution_id, tenant.user_id, **payload.model_dump())
    return ApiResponse(
        data=KnowledgeBaseData.model_validate(row),
        message="Knowledge base created.",
        request_id=request.state.request_id,
    )


@router.get("/documents", response_model=ApiResponse[list[KnowledgeDocumentData]])
async def list_documents(
    request: Request,
    tenant: TenantContext = Depends(require_permission("knowledge.read")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    rows = await KnowledgeRepository(db).list_documents(tenant.institution_id, _limit(limit), _offset(offset))
    return ApiResponse(
        data=[KnowledgeDocumentData.model_validate(row) for row in rows],
        message="Knowledge documents loaded.",
        request_id=request.state.request_id,
    )


@router.post("/documents", response_model=ApiResponse[KnowledgeDocumentData], status_code=201)
async def create_document(
    payload: KnowledgeDocumentCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("knowledge.manage")),
    db: AsyncSession = Depends(get_db),
):
    row = await KnowledgeService(db).create_document(tenant.institution_id, tenant.user_id, **payload.model_dump())
    return ApiResponse(
        data=KnowledgeDocumentData.model_validate(row),
        message="Knowledge document created.",
        request_id=request.state.request_id,
    )


@router.post("/documents/{document_id}/ingest", response_model=ApiResponse[KnowledgeDocumentIngestData], status_code=202)
async def ingest_document(
    document_id: UUID,
    request: Request,
    tenant: TenantContext = Depends(require_permission("knowledge.manage")),
    db: AsyncSession = Depends(get_db),
):
    document, job = await KnowledgeService(db).ingest_document(
        tenant.institution_id,
        tenant.user_id,
        document_id,
        idempotency_key=request.headers.get("Idempotency-Key"),
    )
    return ApiResponse(
        data=KnowledgeDocumentIngestData(
            document=KnowledgeDocumentData.model_validate(document),
            job=BackgroundJobData.model_validate(job),
        ),
        message="Knowledge document ingestion queued.",
        request_id=request.state.request_id,
    )


@router.get("/documents/{document_id}/chunks", response_model=ApiResponse[list[KnowledgeChunkData]])
async def list_chunks(
    document_id: UUID,
    request: Request,
    tenant: TenantContext = Depends(require_permission("knowledge.read")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    rows = await KnowledgeRepository(db).list_chunks(tenant.institution_id, document_id, _limit(limit), _offset(offset))
    return ApiResponse(
        data=[KnowledgeChunkData.model_validate(row) for row in rows],
        message="Knowledge chunks loaded.",
        request_id=request.state.request_id,
    )


@router.post("/search", response_model=ApiResponse[RetrievalSearchData])
async def search_knowledge(
    payload: RetrievalSearchRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("knowledge.read")),
    db: AsyncSession = Depends(get_db),
):
    values = payload.model_dump(mode="json")
    query = values.pop("query")
    feature = values.pop("feature")
    limit = values.pop("limit")
    chunks, filters = await KnowledgeService(db).search(
        tenant.institution_id,
        tenant.user_id,
        query=query,
        feature=feature,
        limit=limit,
        **values,
    )
    return ApiResponse(
        data=RetrievalSearchData(
            chunks=[KnowledgeChunkData.model_validate(row) for row in chunks],
            filters=filters,
        ),
        message="Knowledge search completed.",
        request_id=request.state.request_id,
    )


def _limit(value: int) -> int:
    return max(1, min(value, 100))


def _offset(value: int) -> int:
    return max(0, value)
