# Phase 6 Background Jobs And Queue Foundation

Implemented:

- Durable job status tables:
  - `background_jobs`
  - `job_events`
  - `scheduled_jobs`
- Job statuses:
  - `queued`
  - `running`
  - `retrying`
  - `completed`
  - `failed`
  - `cancelled`
- Tenant-scoped job APIs:
  - `GET /api/v1/jobs`
  - `GET /api/v1/jobs/{job_id}`
  - `POST /api/v1/jobs/{job_id}/cancel`
- Permission seeds:
  - `jobs.read`
  - `jobs.manage`
- Reusable `JobsService.create_and_enqueue(...)` for modules that must return `job_id`.
- Reusable worker status methods:
  - `mark_running`
  - `update_progress`
  - `mark_retrying`
  - `mark_completed`
  - `mark_failed`
- Celery placeholder task for worker lifecycle validation.
- Local Docker Compose worker split:
  - `celery_general_worker`
  - `celery_ai_worker`
  - `celery_rag_worker`
  - `celery_embedding_worker`
  - `celery_ocr_worker`
  - `celery_pdf_worker`
  - `celery_answer_checking_worker`
  - `celery_report_worker`
  - `celery_email_worker`
  - `celery_notification_worker`
  - `celery_analytics_worker`
  - `celery_beat_scheduler`

Queue rules:

- Main API requests create a database job and enqueue Celery work.
- Heavy modules must return `job_id` instead of blocking the request.
- Frontend should poll `GET /api/v1/jobs/{job_id}` until terminal state.
- Worker tasks must update job status and append `job_events`.
- Cancel requests revoke the Celery task when a task id exists and mark the job as `cancelled`.

Deferred to later module phases:

- Real AI/RAG/OCR/PDF/report/email/analytics task implementations.
- Queue depth metrics endpoint.
- Dead-letter exchange wiring.
- Distributed idempotency locks.
- Worker autoscaling manifests.
- Beat schedule registry UI.

