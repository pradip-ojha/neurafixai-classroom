from fastapi import APIRouter, Request, Response, status

from app.schemas.health import HealthResponse, ReadyResponse
from app.services.health_service import check_redis

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    return HealthResponse(
        service="ai_service",
        status="ok",
        request_id=request.state.request_id,
    )


@router.get("/ready", response_model=ReadyResponse)
async def ready(request: Request, response: Response) -> ReadyResponse:
    redis = await check_redis()
    ready_status = "ready" if redis.ok else "not_ready"

    if ready_status != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadyResponse(
        service="ai_service",
        status=ready_status,
        request_id=request.state.request_id,
        dependencies=[redis],
    )


@router.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(
        content="# Prometheus metrics endpoint placeholder for Phase 1\n",
        media_type="text/plain; version=0.0.4",
    )

