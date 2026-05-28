from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIConversation, AIMessage, AIMessageCitation
from app.repositories.tutor_repository import TutorRepository
from app.services.ai_control_service import AIControlService
from app.services.knowledge_service import KnowledgeService


class TutorService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TutorRepository(session)
        self.ai = AIControlService(session)
        self.knowledge = KnowledgeService(session)

    async def create_conversation(self, institution_id: UUID, user_id: UUID, **values) -> AIConversation:
        conversation = AIConversation(institution_id=institution_id, user_id=user_id, **values)
        self.repo.add(conversation)
        await self.repo.commit()
        return conversation

    async def ask(
        self,
        *,
        institution_id: UUID,
        user_id: UUID,
        request_id: str,
        question: str,
        conversation_id: UUID | None,
        title: str | None,
        knowledge_base_id: UUID | None,
        class_id: UUID | None,
        subject_id: UUID | None,
        chapter_id: UUID | None,
        topic_id: UUID | None,
        model_config_id: UUID | None,
        metadata: dict | None,
    ):
        conversation = None
        if conversation_id:
            conversation = await self.repo.get_conversation(institution_id, user_id, conversation_id)
            if not conversation:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Tutor conversation not found")
        else:
            conversation = AIConversation(
                institution_id=institution_id,
                user_id=user_id,
                title=title or question[:80],
                class_id=class_id,
                subject_id=subject_id,
                chapter_id=chapter_id,
                topic_id=topic_id,
            )
            self.repo.add(conversation)
            await self.repo.flush()

        user_message = AIMessage(
            institution_id=institution_id,
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=question,
        )
        self.repo.add(user_message)
        await self.repo.flush()

        chunks, filters = await self.knowledge.search(
            institution_id,
            user_id,
            query=question,
            feature="ai_tutor.use",
            limit=5,
            knowledge_base_id=knowledge_base_id,
            class_id=class_id or conversation.class_id,
            subject_id=subject_id or conversation.subject_id,
            chapter_id=chapter_id or conversation.chapter_id,
            topic_id=topic_id or conversation.topic_id,
            approved_only=True,
        )
        prompt = _build_tutor_prompt(question, [chunk.text for chunk in chunks])
        json_filters = _json_safe(filters)
        ai_result = await self.ai.generate_text(
            institution_id=institution_id,
            user_id=user_id,
            request_id=request_id,
            prompt=prompt,
            feature="ai_tutor.use",
            model_config_id=model_config_id,
            metadata={
                "conversation_id": str(conversation.id),
                "retrieval_filters": json_filters,
                **(metadata or {}),
            },
        )
        assistant_message = AIMessage(
            institution_id=institution_id,
            conversation_id=conversation.id,
            user_id=None,
            role="assistant",
            content=ai_result["text"],
            provider=ai_result["provider"],
            model_name=ai_result["model_name"],
            prompt_tokens=ai_result["prompt_tokens"],
            completion_tokens=ai_result["completion_tokens"],
            total_tokens=ai_result["total_tokens"],
            estimated_cost_cents=ai_result["estimated_cost_cents"],
            latency_ms=ai_result["latency_ms"],
            metadata_json={"retrieved_chunk_ids": [str(chunk.id) for chunk in chunks]},
        )
        self.repo.add(assistant_message)
        await self.repo.flush()

        citations = []
        for index, chunk in enumerate(chunks, start=1):
            citation = AIMessageCitation(
                institution_id=institution_id,
                message_id=assistant_message.id,
                knowledge_chunk_id=chunk.id,
                rank=index,
                citation_text=chunk.text[:500],
            )
            self.repo.add(citation)
            citations.append(citation)

        await self.repo.commit()
        return conversation, user_message, assistant_message, citations


def _build_tutor_prompt(question: str, context_chunks: list[str]) -> str:
    if context_chunks:
        context = "\n\n".join(f"Source {index}: {text}" for index, text in enumerate(context_chunks, start=1))
    else:
        context = "No approved school knowledge chunks were retrieved."
    return (
        "You are NeuraFix School OS AI Tutor. Answer only using approved school context when it is relevant. "
        "If the context is missing, say what is missing and give a careful general explanation.\n\n"
        f"Approved context:\n{context}\n\n"
        f"Student question:\n{question}\n\n"
        "Return a clear educational answer with brief citations like [Source 1] when using context."
    )


def _json_safe(values: dict) -> dict:
    safe = {}
    for key, value in values.items():
        if isinstance(value, UUID):
            safe[key] = str(value)
        else:
            safe[key] = value
    return safe
