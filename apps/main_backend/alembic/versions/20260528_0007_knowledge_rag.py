"""knowledge rag foundation

Revision ID: 20260528_0007
Revises: 20260528_0006
Create Date: 2026-05-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260528_0007"
down_revision: Union[str, None] = "20260528_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_bases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("vector_namespace", sa.String(length=180), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("institution_id", "slug", name="uq_knowledge_bases_institution_slug"),
    )
    op.create_index("ix_knowledge_bases_institution_active", "knowledge_bases", ["institution_id", "is_active"])

    op.create_table(
        "knowledge_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("knowledge_base_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_object_id", postgresql.UUID(as_uuid=True)),
        sa.Column("content_item_id", postgresql.UUID(as_uuid=True)),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=60), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True)),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True)),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True)),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True)),
        sa.Column("subtopic_id", postgresql.UUID(as_uuid=True)),
        sa.Column("language", sa.String(length=20), nullable=False, server_default="en"),
        sa.Column("visibility", sa.String(length=40), nullable=False, server_default="institution"),
        sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("index_status", sa.String(length=40), nullable=False, server_default="pending"),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata_json", postgresql.JSONB()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("indexed_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["knowledge_base_id"], ["knowledge_bases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["file_object_id"], ["file_objects.id"]),
        sa.ForeignKeyConstraint(["content_item_id"], ["content_items.id"]),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["chapter_id"], ["syllabus_chapters.id"]),
        sa.ForeignKeyConstraint(["topic_id"], ["syllabus_topics.id"]),
        sa.ForeignKeyConstraint(["subtopic_id"], ["syllabus_subtopics.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
    )
    op.create_index(
        "ix_knowledge_documents_base_status",
        "knowledge_documents",
        ["institution_id", "knowledge_base_id", "index_status"],
    )
    op.create_index(
        "ix_knowledge_documents_scope",
        "knowledge_documents",
        ["institution_id", "class_id", "subject_id", "chapter_id"],
    )

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("knowledge_base_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("knowledge_document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer()),
        sa.Column("vector_namespace", sa.String(length=180), nullable=False),
        sa.Column("vector_id", sa.String(length=220)),
        sa.Column("embedding_status", sa.String(length=40), nullable=False, server_default="pending"),
        sa.Column("metadata_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["knowledge_document_id"], ["knowledge_documents.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("knowledge_document_id", "chunk_index", name="uq_knowledge_chunks_document_index"),
    )
    op.create_index("ix_knowledge_chunks_document", "knowledge_chunks", ["institution_id", "knowledge_document_id"])
    op.create_index("ix_knowledge_chunks_vector", "knowledge_chunks", ["vector_namespace", "vector_id"])

    op.create_table(
        "embedding_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("knowledge_document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("background_job_id", postgresql.UUID(as_uuid=True)),
        sa.Column("provider", sa.String(length=80), nullable=False, server_default="openai_compatible"),
        sa.Column("embedding_model", sa.String(length=160), nullable=False, server_default="text-embedding-3-small"),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="queued"),
        sa.Column("chunks_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("chunks_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["knowledge_document_id"], ["knowledge_documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["background_job_id"], ["background_jobs.id"]),
    )
    op.create_index(
        "ix_embedding_jobs_document_status",
        "embedding_jobs",
        ["institution_id", "knowledge_document_id", "status"],
    )

    op.create_table(
        "retrieval_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("feature", sa.String(length=80), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("filters_json", postgresql.JSONB()),
        sa.Column("result_chunk_ids", postgresql.JSONB()),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_retrieval_logs_institution_user_created",
        "retrieval_logs",
        ["institution_id", "user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_retrieval_logs_institution_user_created", table_name="retrieval_logs")
    op.drop_table("retrieval_logs")
    op.drop_index("ix_embedding_jobs_document_status", table_name="embedding_jobs")
    op.drop_table("embedding_jobs")
    op.drop_index("ix_knowledge_chunks_vector", table_name="knowledge_chunks")
    op.drop_index("ix_knowledge_chunks_document", table_name="knowledge_chunks")
    op.drop_table("knowledge_chunks")
    op.drop_index("ix_knowledge_documents_scope", table_name="knowledge_documents")
    op.drop_index("ix_knowledge_documents_base_status", table_name="knowledge_documents")
    op.drop_table("knowledge_documents")
    op.drop_index("ix_knowledge_bases_institution_active", table_name="knowledge_bases")
    op.drop_table("knowledge_bases")
