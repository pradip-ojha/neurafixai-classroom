from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_permission
from app.core.tenant import TenantContext
from app.db.session import get_db
from app.repositories.ai_repository import AIRepository
from app.schemas.ai import (
    AIModelConfigCreateRequest,
    AIModelConfigData,
    AITextGenerationData,
    AITextGenerationRequest,
    InstitutionAILimitData,
    InstitutionAILimitUpdateRequest,
    PromptTemplateCreateRequest,
    PromptTemplateData,
)
from app.schemas.common import ApiResponse
from app.schemas.tutor import (
    TutorAskData,
    TutorAskRequest,
    TutorCitationData,
    TutorConversationCreateRequest,
    TutorConversationData,
    TutorMessageData,
)
from app.services.ai_control_service import AIControlService
from app.services.tutor_service import TutorService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/model-configs", response_model=ApiResponse[list[AIModelConfigData]])
async def list_model_configs(
    request: Request,
    tenant: TenantContext = Depends(require_permission("ai_tutor.configure")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[AIModelConfigData]]:
    rows = await AIRepository(db).list_model_configs(tenant.institution_id)
    return ApiResponse(
        data=[AIModelConfigData.model_validate(row) for row in rows],
        message="AI model configs loaded.",
        request_id=request.state.request_id,
    )


@router.post("/model-configs", response_model=ApiResponse[AIModelConfigData], status_code=201)
async def create_model_config(
    payload: AIModelConfigCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("ai_tutor.configure")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AIModelConfigData]:
    row = await AIControlService(db).create_model_config(tenant.institution_id, **payload.model_dump())
    return ApiResponse(
        data=AIModelConfigData.model_validate(row),
        message="AI model config created.",
        request_id=request.state.request_id,
    )


@router.get("/limits", response_model=ApiResponse[InstitutionAILimitData])
async def get_ai_limits(
    request: Request,
    tenant: TenantContext = Depends(require_permission("ai_tutor.configure")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[InstitutionAILimitData]:
    row = await AIControlService(db).get_or_create_limits(tenant.institution_id)
    return ApiResponse(
        data=InstitutionAILimitData.model_validate(row),
        message="AI limits loaded.",
        request_id=request.state.request_id,
    )


@router.patch("/limits", response_model=ApiResponse[InstitutionAILimitData])
async def update_ai_limits(
    payload: InstitutionAILimitUpdateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("ai_tutor.configure")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[InstitutionAILimitData]:
    row = await AIControlService(db).update_limits(tenant.institution_id, **payload.model_dump())
    return ApiResponse(
        data=InstitutionAILimitData.model_validate(row),
        message="AI limits updated.",
        request_id=request.state.request_id,
    )


@router.get("/prompt-templates", response_model=ApiResponse[list[PromptTemplateData]])
async def list_prompt_templates(
    request: Request,
    tenant: TenantContext = Depends(require_permission("ai_tutor.configure")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[PromptTemplateData]]:
    rows = await AIRepository(db).list_prompt_templates(tenant.institution_id)
    return ApiResponse(
        data=[PromptTemplateData.model_validate(row) for row in rows],
        message="Prompt templates loaded.",
        request_id=request.state.request_id,
    )


@router.post("/prompt-templates", response_model=ApiResponse[PromptTemplateData], status_code=201)
async def create_prompt_template(
    payload: PromptTemplateCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("ai_tutor.configure")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PromptTemplateData]:
    row = await AIControlService(db).create_prompt_template(
        tenant.institution_id,
        tenant.user_id,
        **payload.model_dump(),
    )
    return ApiResponse(
        data=PromptTemplateData.model_validate(row),
        message="Prompt template created.",
        request_id=request.state.request_id,
    )


@router.post("/generate-text", response_model=ApiResponse[AITextGenerationData])
async def generate_text(
    payload: AITextGenerationRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("ai_content.generate")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AITextGenerationData]:
    result = await AIControlService(db).generate_text(
        institution_id=tenant.institution_id,
        user_id=tenant.user_id,
        request_id=request.state.request_id,
        **payload.model_dump(),
    )
    return ApiResponse(
        data=AITextGenerationData(**result),
        message="AI text generated.",
        request_id=request.state.request_id,
    )


@router.get("/tutor/conversations", response_model=ApiResponse[list[TutorConversationData]])
async def list_tutor_conversations(
    request: Request,
    tenant: TenantContext = Depends(require_permission("ai_tutor.use")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> ApiResponse[list[TutorConversationData]]:
    rows = await TutorService(db).repo.list_conversations(
        tenant.institution_id,
        tenant.user_id,
        _limit(limit),
        _offset(offset),
    )
    return ApiResponse(
        data=[TutorConversationData.model_validate(row) for row in rows],
        message="Tutor conversations loaded.",
        request_id=request.state.request_id,
    )


@router.post("/tutor/conversations", response_model=ApiResponse[TutorConversationData], status_code=201)
async def create_tutor_conversation(
    payload: TutorConversationCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("ai_tutor.use")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TutorConversationData]:
    row = await TutorService(db).create_conversation(tenant.institution_id, tenant.user_id, **payload.model_dump())
    return ApiResponse(
        data=TutorConversationData.model_validate(row),
        message="Tutor conversation created.",
        request_id=request.state.request_id,
    )


@router.get("/tutor/conversations/{conversation_id}/messages", response_model=ApiResponse[list[TutorMessageData]])
async def list_tutor_messages(
    conversation_id: UUID,
    request: Request,
    tenant: TenantContext = Depends(require_permission("ai_tutor.use")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> ApiResponse[list[TutorMessageData]]:
    conversation = await TutorService(db).repo.get_conversation(tenant.institution_id, tenant.user_id, conversation_id)
    if not conversation:
        from fastapi import HTTPException, status

        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tutor conversation not found")
    rows = await TutorService(db).repo.list_messages(tenant.institution_id, conversation_id, _limit(limit), _offset(offset))
    return ApiResponse(
        data=[TutorMessageData.model_validate(row) for row in rows],
        message="Tutor messages loaded.",
        request_id=request.state.request_id,
    )


@router.post("/tutor/ask", response_model=ApiResponse[TutorAskData])
async def ask_tutor(
    payload: TutorAskRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("ai_tutor.use")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TutorAskData]:
    conversation, user_message, assistant_message, citations = await TutorService(db).ask(
        institution_id=tenant.institution_id,
        user_id=tenant.user_id,
        request_id=request.state.request_id,
        **payload.model_dump(),
    )
    return ApiResponse(
        data=TutorAskData(
            conversation=TutorConversationData.model_validate(conversation),
            user_message=TutorMessageData.model_validate(user_message),
            assistant_message=TutorMessageData.model_validate(assistant_message),
            citations=[TutorCitationData.model_validate(row) for row in citations],
        ),
        message="Tutor answer generated.",
        request_id=request.state.request_id,
    )


def _limit(value: int) -> int:
    return max(1, min(value, 100))


def _offset(value: int) -> int:
    return max(0, value)
