# Phase 9 AI Tutor

Implemented:

- Tenant-scoped tutor conversation tables:
  - `ai_conversations`
  - `ai_messages`
  - `ai_message_citations`
- Tutor APIs:
  - `GET /api/v1/ai/tutor/conversations`
  - `POST /api/v1/ai/tutor/conversations`
  - `GET /api/v1/ai/tutor/conversations/{conversation_id}/messages`
  - `POST /api/v1/ai/tutor/ask`
- RAG-backed answer flow:
  - Save user message.
  - Retrieve approved tenant knowledge chunks.
  - Build a grounded tutor prompt.
  - Call the AI service through the backend control plane.
  - Record AI usage and safety events through Phase 7 infrastructure.
  - Save assistant message.
  - Save citations to `knowledge_chunks`.
- Permission:
  - `ai_tutor.use`

Security and tenant rules:

- The frontend does not provide authoritative `institution_id`.
- Conversations are scoped by `institution_id` and `user_id`.
- Users can only list and read their own tutor conversations.
- Retrieval uses tenant-scoped chunks and approved content filters.
- Usage and safety logging remains centralized in the backend.

Deferred:

- Streaming tutor responses.
- Real vector retrieval and reranking.
- Prompt template rendering.
- Parent/teacher/student relationship-specific access rules.
- Conversation summarization.
- Long-running tutor jobs for expensive requests.
- Citation hydration with full document titles and page numbers.

