# Phase 1 Architecture Baseline

Phase 1 establishes the deployable shape of NeuraFix School OS without implementing business workflows.

## Built In This Phase

- Monorepo structure
- Main FastAPI backend
- AI FastAPI service
- Next.js frontend shell
- PostgreSQL, Redis, RabbitMQ local stack
- Celery queue configuration
- Health and readiness endpoints
- Alembic wiring
- Structured JSON logging
- Starter tests

## Explicitly Deferred

- Authentication and refresh token rotation
- RBAC and tenant-scoped data models
- Institution, student, teacher, and parent modules
- Content, files, exams, AI tutor, RAG, OCR, reports, analytics

## Non-Negotiable Rule

All heavy work in future phases must return a `job_id` and run through Celery workers.

