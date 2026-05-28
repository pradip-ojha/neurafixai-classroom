"""syllabus content and file metadata

Revision ID: 20260528_0004
Revises: 20260528_0003
Create Date: 2026-05-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260528_0004"
down_revision: Union[str, None] = "20260528_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def tenant_uuid_column() -> sa.Column:
    return sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False)


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    ]


def upgrade() -> None:
    op.create_table(
        "syllabus_chapters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        tenant_uuid_column(),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("sequence", sa.Integer(), nullable=False, server_default="0"),
        *timestamps(),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.UniqueConstraint("institution_id", "class_id", "subject_id", "name", name="uq_syllabus_chapters_scope_name"),
    )
    op.create_index("ix_syllabus_chapters_scope", "syllabus_chapters", ["institution_id", "class_id", "subject_id"])

    op.create_table(
        "syllabus_topics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        tenant_uuid_column(),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("sequence", sa.Integer(), nullable=False, server_default="0"),
        *timestamps(),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["chapter_id"], ["syllabus_chapters.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", "chapter_id", "name", name="uq_syllabus_topics_chapter_name"),
    )
    op.create_index("ix_syllabus_topics_chapter", "syllabus_topics", ["institution_id", "chapter_id"])

    op.create_table(
        "syllabus_subtopics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        tenant_uuid_column(),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("sequence", sa.Integer(), nullable=False, server_default="0"),
        *timestamps(),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["topic_id"], ["syllabus_topics.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", "topic_id", "name", name="uq_syllabus_subtopics_topic_name"),
    )
    op.create_index("ix_syllabus_subtopics_topic", "syllabus_subtopics", ["institution_id", "topic_id"])

    op.create_table(
        "learning_objectives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        tenant_uuid_column(),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True)),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True)),
        sa.Column("subtopic_id", postgresql.UUID(as_uuid=True)),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False, server_default="0"),
        *timestamps(),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["chapter_id"], ["syllabus_chapters.id"]),
        sa.ForeignKeyConstraint(["topic_id"], ["syllabus_topics.id"]),
        sa.ForeignKeyConstraint(["subtopic_id"], ["syllabus_subtopics.id"]),
    )
    op.create_index(
        "ix_learning_objectives_scope",
        "learning_objectives",
        ["institution_id", "chapter_id", "topic_id", "subtopic_id"],
    )

    op.create_table(
        "file_objects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        tenant_uuid_column(),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("bucket", sa.String(length=120), nullable=False),
        sa.Column("object_key", sa.String(length=700), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=160), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=160)),
        sa.Column("visibility", sa.String(length=40), nullable=False, server_default="private"),
        sa.Column("scan_status", sa.String(length=40), nullable=False, server_default="pending"),
        sa.Column("processing_status", sa.String(length=40), nullable=False, server_default="pending"),
        sa.Column("metadata_json", postgresql.JSONB()),
        *timestamps(),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
    )
    op.create_index("ix_file_objects_owner", "file_objects", ["institution_id", "owner_user_id", "created_at"])
    op.create_index("ix_file_objects_key", "file_objects", ["bucket", "object_key"])

    op.create_table(
        "content_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        tenant_uuid_column(),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="draft"),
        sa.Column("visibility", sa.String(length=40), nullable=False, server_default="institution"),
        sa.Column("class_id", postgresql.UUID(as_uuid=True)),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True)),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True)),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True)),
        sa.Column("subtopic_id", postgresql.UUID(as_uuid=True)),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("current_version_id", postgresql.UUID(as_uuid=True)),
        *timestamps(),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["chapter_id"], ["syllabus_chapters.id"]),
        sa.ForeignKeyConstraint(["topic_id"], ["syllabus_topics.id"]),
        sa.ForeignKeyConstraint(["subtopic_id"], ["syllabus_subtopics.id"]),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
    )
    op.create_index("ix_content_items_scope", "content_items", ["institution_id", "class_id", "subject_id", "chapter_id"])
    op.create_index("ix_content_items_status", "content_items", ["institution_id", "status", "created_at"])

    op.create_table(
        "content_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        tenant_uuid_column(),
        sa.Column("content_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text()),
        sa.Column("summary", sa.Text()),
        sa.Column("metadata_json", postgresql.JSONB()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["content_item_id"], ["content_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("content_item_id", "version_number", name="uq_content_versions_item_number"),
    )
    op.create_index("ix_content_versions_item", "content_versions", ["institution_id", "content_item_id"])

    op.create_table(
        "content_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        tenant_uuid_column(),
        sa.Column("content_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_object_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=60), nullable=False, server_default="attachment"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["content_item_id"], ["content_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["file_object_id"], ["file_objects.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("content_item_id", "file_object_id", name="uq_content_files_item_file"),
    )
    op.create_index("ix_content_files_item", "content_files", ["institution_id", "content_item_id"])

    op.create_table(
        "content_tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        tenant_uuid_column(),
        sa.Column("content_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["content_item_id"], ["content_items.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", "content_item_id", "tag", name="uq_content_tags_item_tag"),
    )
    op.create_index("ix_content_tags_tag", "content_tags", ["institution_id", "tag"])

    op.create_table(
        "content_approvals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        tenant_uuid_column(),
        sa.Column("content_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("reviewer_user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("comment", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["content_item_id"], ["content_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewer_user_id"], ["users.id"]),
    )
    op.create_index("ix_content_approvals_item", "content_approvals", ["institution_id", "content_item_id", "created_at"])

    op.create_table(
        "file_access_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        tenant_uuid_column(),
        sa.Column("file_object_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("ip_address", sa.String(length=80)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["file_object_id"], ["file_objects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
    )
    op.create_index("ix_file_access_logs_file_created", "file_access_logs", ["institution_id", "file_object_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_file_access_logs_file_created", table_name="file_access_logs")
    op.drop_table("file_access_logs")
    op.drop_index("ix_content_approvals_item", table_name="content_approvals")
    op.drop_table("content_approvals")
    op.drop_index("ix_content_tags_tag", table_name="content_tags")
    op.drop_table("content_tags")
    op.drop_index("ix_content_files_item", table_name="content_files")
    op.drop_table("content_files")
    op.drop_index("ix_content_versions_item", table_name="content_versions")
    op.drop_table("content_versions")
    op.drop_index("ix_content_items_status", table_name="content_items")
    op.drop_index("ix_content_items_scope", table_name="content_items")
    op.drop_table("content_items")
    op.drop_index("ix_file_objects_key", table_name="file_objects")
    op.drop_index("ix_file_objects_owner", table_name="file_objects")
    op.drop_table("file_objects")
    op.drop_index("ix_learning_objectives_scope", table_name="learning_objectives")
    op.drop_table("learning_objectives")
    op.drop_index("ix_syllabus_subtopics_topic", table_name="syllabus_subtopics")
    op.drop_table("syllabus_subtopics")
    op.drop_index("ix_syllabus_topics_chapter", table_name="syllabus_topics")
    op.drop_table("syllabus_topics")
    op.drop_index("ix_syllabus_chapters_scope", table_name="syllabus_chapters")
    op.drop_table("syllabus_chapters")
