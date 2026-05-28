from fastapi import APIRouter

from app.api.v1.routes import health, internal

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(health.router, prefix="/api/v1")
api_router.include_router(internal.router, prefix="/api/v1")
