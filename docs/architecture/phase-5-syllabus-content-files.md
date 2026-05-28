# Phase 5 Syllabus, Content, And Files

Implemented:

- Tenant-scoped syllabus hierarchy:
  - `syllabus_chapters`
  - `syllabus_topics`
  - `syllabus_subtopics`
  - `learning_objectives`
- Tenant-scoped content metadata:
  - `content_items`
  - `content_versions`
  - `content_files`
  - `content_tags`
  - `content_approvals`
- Tenant-scoped file metadata:
  - `file_objects`
  - `file_access_logs`
- Signed upload/download URL abstraction.
- Object key pattern: `institutions/{institution_id}/{module}/{entity_id}/{file_id}.{ext}`.
- API routes:
  - `GET/POST /api/v1/syllabus/chapters`
  - `GET/POST /api/v1/syllabus/topics`
  - `GET/POST /api/v1/syllabus/subtopics`
  - `GET/POST /api/v1/syllabus/objectives`
  - `GET/POST /api/v1/content/items`
  - `POST /api/v1/content/items/{content_item_id}/versions`
  - `POST /api/v1/content/items/{content_item_id}/approval`
  - `POST /api/v1/files/upload-url`
  - `GET /api/v1/files/{file_id}/download-url`

Security rules:

- Endpoints derive `institution_id` from the authenticated session.
- Frontend-provided `institution_id` is not accepted.
- Protected endpoints use backend permission checks:
  - `syllabus.manage`
  - `content.read`
  - `content.upload`
  - `content.update`
  - `content.approve`
  - `files.upload`
  - `files.download`
- File access URL creation is logged in `file_access_logs`.

Deferred to Phase 6:

- Durable `background_jobs` and `job_events`.
- RAG ingestion job creation.
- Embedding generation queues.
- OCR/PDF processing queues.
- Object storage SDK integration.
- Malware scan worker.
- File lifecycle cleanup worker.

