# Phase 1 API

## Main Backend

```text
GET /health
GET /ready
GET /api/v1/health
GET /api/v1/ready
```

## AI Service

```text
GET /health
GET /ready
GET /api/v1/health
GET /api/v1/ready
```

Readiness checks external dependencies and returns HTTP `503` when a required dependency is unavailable.

## Added In Later Phases

```text
GET /api/v1/jobs
GET /api/v1/jobs/{job_id}
POST /api/v1/jobs/{job_id}/cancel
GET /api/v1/ai/model-configs
POST /api/v1/ai/model-configs
GET /api/v1/ai/limits
PATCH /api/v1/ai/limits
GET /api/v1/ai/prompt-templates
POST /api/v1/ai/prompt-templates
POST /api/v1/ai/generate-text
GET /api/v1/knowledge-base/bases
POST /api/v1/knowledge-base/bases
GET /api/v1/knowledge-base/documents
POST /api/v1/knowledge-base/documents
POST /api/v1/knowledge-base/documents/{document_id}/ingest
GET /api/v1/knowledge-base/documents/{document_id}/chunks
POST /api/v1/knowledge-base/search
GET /api/v1/ai/tutor/conversations
POST /api/v1/ai/tutor/conversations
GET /api/v1/ai/tutor/conversations/{conversation_id}/messages
POST /api/v1/ai/tutor/ask
```

Long-running workflows should create `background_jobs` rows and return `job_id` to the frontend.
