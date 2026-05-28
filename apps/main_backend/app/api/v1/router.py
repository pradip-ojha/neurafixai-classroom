from fastapi import APIRouter

from app.api.v1.routes import ai, auth, content, core, files, health, jobs, knowledge, rbac, syllabus

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(health.router, prefix="/api/v1")
api_router.include_router(auth.router, prefix="/api/v1")
api_router.include_router(core.router, prefix="/api/v1")
api_router.include_router(rbac.router, prefix="/api/v1")
api_router.include_router(syllabus.router, prefix="/api/v1")
api_router.include_router(content.router, prefix="/api/v1")
api_router.include_router(files.router, prefix="/api/v1")
api_router.include_router(jobs.router, prefix="/api/v1")
api_router.include_router(ai.router, prefix="/api/v1")
api_router.include_router(knowledge.router, prefix="/api/v1")
