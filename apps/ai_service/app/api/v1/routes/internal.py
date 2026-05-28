from fastapi import APIRouter, Depends

from app.api.dependencies import require_internal_service
from app.schemas.generation import TextGenerationRequest, TextGenerationResponse
from app.schemas.retrieval import RetrievalSearchRequest, RetrievalSearchResponse
from app.services.generation_service import GenerationService
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/internal", tags=["internal-ai"], dependencies=[Depends(require_internal_service)])


@router.post("/generate/text", response_model=TextGenerationResponse)
async def generate_text(payload: TextGenerationRequest) -> TextGenerationResponse:
    return await GenerationService().generate_text(payload)


@router.post("/retrieval/search", response_model=RetrievalSearchResponse)
async def search_retrieval(payload: RetrievalSearchRequest) -> RetrievalSearchResponse:
    return await RetrievalService().search(payload)
