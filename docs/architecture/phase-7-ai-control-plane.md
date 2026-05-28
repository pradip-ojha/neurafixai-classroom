# Phase 7 AI Control Plane

Implemented:

- Main backend AI control tables:
  - `ai_model_configs`
  - `institution_ai_limits`
  - `ai_usage_logs`
  - `prompt_templates`
  - `prompt_versions`
  - `ai_safety_events`
- Main backend AI APIs:
  - `GET/POST /api/v1/ai/model-configs`
  - `GET/PATCH /api/v1/ai/limits`
  - `GET/POST /api/v1/ai/prompt-templates`
  - `POST /api/v1/ai/generate-text`
- Backend-to-AI-service internal client.
- AI service internal-only route:
  - `POST /api/v1/internal/generate/text`
- OpenAI-compatible provider abstraction.
- Local development provider fallback when no provider key/base URL is configured.
- Basic prompt-injection safety filter.
- AI usage logging with token and estimated cost fields.
- Tenant AI daily limit checks before provider calls.

Security rules:

- Frontend must not call the AI service directly.
- AI service internal endpoints require `X-Internal-Service-Token`.
- Backend derives `institution_id` and `user_id` from the authenticated session.
- Backend logs usage and safety events per tenant/user.
- Prompt templates and model configs are tenant-scoped.

Deferred:

- Streaming responses.
- RAG context building.
- Vector database retrieval.
- Prompt variable rendering.
- Provider cost calculation by model.
- Monthly quota enforcement.
- AI tutor conversations and messages.
- AI content generation jobs for long-running tasks.

