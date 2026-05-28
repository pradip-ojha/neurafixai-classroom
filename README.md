# NeuraFix School OS

Production-grade multi-tenant AI School OS foundation.

Phase 1 provides the service skeleton and local development stack only:

- Next.js frontend shell
- FastAPI main backend
- FastAPI AI service
- PostgreSQL
- Redis
- RabbitMQ
- Celery worker entrypoints
- Alembic wiring
- Structured logging
- Health and readiness endpoints
- Starter tests

Business modules start in Phase 2 after this foundation is approved.

## Local Development

Optional: copy the environment file if you want to override local defaults:

```bash
cp .env.example .env
```

Start the local stack:

```bash
docker compose -f docker-compose.local.yml up --build
```

Service URLs:

- Frontend: http://localhost:3000
- Main backend: http://localhost:8000
- AI service: http://localhost:8001
- RabbitMQ management: http://localhost:15672

Health checks:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8001/health
curl http://localhost:8001/ready
```

## Phase Discipline

The system is intentionally built in phases. Phase 1 should not include auth, RBAC, tenant business tables, exams, RAG, or answer-sheet checking logic. Those arrive in later phases with migrations, tests, and security checks.
