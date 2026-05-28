# Phase 8 RAG And Knowledge Layer

Implemented:

- PostgreSQL source-of-truth tables:
  - `knowledge_bases`
  - `knowledge_documents`
  - `knowledge_chunks`
  - `embedding_jobs`
  - `retrieval_logs`
- Tenant-scoped backend APIs:
  - `GET/POST /api/v1/knowledge-base/bases`
  - `GET/POST /api/v1/knowledge-base/documents`
  - `POST /api/v1/knowledge-base/documents/{document_id}/ingest`
  - `GET /api/v1/knowledge-base/documents/{document_id}/chunks`
  - `POST /api/v1/knowledge-base/search`
- Permission seeds:
  - `knowledge.read`
  - `knowledge.manage`
- Queue-based document ingestion contract:
  - API marks the document queued.
  - API creates `background_jobs`.
  - API creates `embedding_jobs`.
  - API returns `job_id`.
  - `rag.ingest_document` runs on the `rag_ingestion` queue.
- AI service retrieval boundary:
  - `POST /api/v1/internal/retrieval/search`
  - strict institution namespace validation.
  - Pinecone-ready vector store interface.

Tenant and retrieval rules:

- The frontend never supplies authoritative `institution_id`.
- Backend derives tenant from the authenticated session.
- Knowledge search records `retrieval_logs`.
- Vector namespaces must start with `institution_{institution_id}` for tenant-owned content.
- PostgreSQL chunks remain the rebuildable source of truth.
- Vector DB entries are treated as disposable acceleration data.

Deferred:

- Real text extraction from PDF/image/content sources.
- Real chunking strategy with token windows and overlap.
- Embedding generation worker implementation.
- Pinecone upserts and hybrid vector search.
- PostgreSQL full-text search ranking.
- Reranking.
- Citation hydration into AI tutor responses.
- Global approved shared-content namespace.

