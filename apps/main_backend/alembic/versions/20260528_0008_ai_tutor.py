"""ai tutor conversations

Revision ID: 20260528_0008
Revises: 20260528_0007
Create Date: 2026-05-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260528_0008"
down_revision: Union[str, None] = "20260528_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255)),
        sa.Column("feature", sa.String(length=80), nullable=False, server_default="ai_tutor.use"),
        sa.Column("class_id", postgresql.UUID(as_uuid=True)),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True)),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True)),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True)),
        sa.Column("metadata_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("archived_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["chapter_id"], ["syllabus_chapters.id"]),
        sa.ForeignKeyConstraint(["topic_id"], ["syllabus_topics.id"]),
    )
    op.create_index("ix_ai_conversations_user_created", "ai_conversations", ["institution_id", "user_id", "created_at"])
    op.create_index("ix_ai_conversations_scope", "ai_conversations", ["institution_id", "class_id", "subject_id", "chapter_id"])

    op.create_table(
        "ai_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=80)),
        sa.Column("model_name", sa.String(length=160)),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_cost_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("safety_status", sa.String(length=40), nullable=False, server_default="allowed"),
        sa.Column("metadata_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["conversation_id"], ["ai_conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_ai_messages_conversation_created", "ai_messages", ["institution_id", "conversation_id", "created_at"])

    op.create_table(
        "ai_message_citations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("knowledge_chunk_id", postgresql.UUID(as_uuid=True)),
        sa.Column("rank", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("citation_text", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["message_id"], ["ai_messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["knowledge_chunk_id"], ["knowledge_chunks.id"]),
        sa.UniqueConstraint("message_id", "knowledge_chunk_id", name="uq_ai_message_citations_message_chunk"),
    )
    op.create_index("ix_ai_message_citations_message", "ai_message_citations", ["institution_id", "message_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_message_citations_message", table_name="ai_message_citations")
    op.drop_table("ai_message_citations")
    op.drop_index("ix_ai_messages_conversation_created", table_name="ai_messages")
    op.drop_table("ai_messages")
    op.drop_index("ix_ai_conversations_scope", table_name="ai_conversations")
    op.drop_index("ix_ai_conversations_user_created", table_name="ai_conversations")
    op.drop_table("ai_conversations")
