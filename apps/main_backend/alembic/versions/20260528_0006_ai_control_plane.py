"""ai control plane

Revision ID: 20260528_0006
Revises: 20260528_0005
Create Date: 2026-05-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260528_0006"
down_revision: Union[str, None] = "20260528_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_model_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False, server_default="openai_compatible"),
        sa.Column("model_name", sa.String(length=160), nullable=False),
        sa.Column("task_type", sa.String(length=80), nullable=False),
        sa.Column("max_output_tokens", sa.Integer(), nullable=False, server_default="1024"),
        sa.Column("temperature", sa.Numeric(4, 3), nullable=False, server_default="0.2"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("settings_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("institution_id", "name", name="uq_ai_model_configs_institution_name"),
    )
    op.create_index("ix_ai_model_configs_institution_active", "ai_model_configs", ["institution_id", "is_active"])

    op.create_table(
        "institution_ai_limits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("daily_token_limit", sa.Integer(), nullable=False, server_default="100000"),
        sa.Column("monthly_token_limit", sa.Integer(), nullable=False, server_default="2000000"),
        sa.Column("daily_cost_limit_cents", sa.Integer(), nullable=False, server_default="5000"),
        sa.Column("monthly_cost_limit_cents", sa.Integer(), nullable=False, server_default="100000"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("institution_id", name="uq_institution_ai_limits_institution"),
    )

    op.create_table(
        "ai_usage_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("request_id", sa.String(length=80)),
        sa.Column("feature", sa.String(length=80), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model_name", sa.String(length=160), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_cost_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("metadata_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_ai_usage_logs_institution_user_created",
        "ai_usage_logs",
        ["institution_id", "user_id", "created_at"],
    )
    op.create_index("ix_ai_usage_logs_institution_day", "ai_usage_logs", ["institution_id", "usage_date"])

    op.create_table(
        "prompt_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True)),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("feature", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("active_version_id", postgresql.UUID(as_uuid=True)),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("institution_id", "slug", name="uq_prompt_templates_institution_slug"),
    )
    op.create_index("ix_prompt_templates_institution_feature", "prompt_templates", ["institution_id", "feature"])

    op.create_table(
        "prompt_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True)),
        sa.Column("prompt_template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("user_prompt_template", sa.Text(), nullable=False),
        sa.Column("model_defaults", postgresql.JSONB()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["prompt_template_id"], ["prompt_templates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("prompt_template_id", "version_number", name="uq_prompt_versions_template_version"),
    )
    op.create_index("ix_prompt_versions_template", "prompt_versions", ["institution_id", "prompt_template_id"])

    op.create_table(
        "ai_safety_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("feature", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_ai_safety_events_institution_user_created",
        "ai_safety_events",
        ["institution_id", "user_id", "created_at"],
    )
    op.create_index("ix_ai_safety_events_category", "ai_safety_events", ["institution_id", "category", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_ai_safety_events_category", table_name="ai_safety_events")
    op.drop_index("ix_ai_safety_events_institution_user_created", table_name="ai_safety_events")
    op.drop_table("ai_safety_events")
    op.drop_index("ix_prompt_versions_template", table_name="prompt_versions")
    op.drop_table("prompt_versions")
    op.drop_index("ix_prompt_templates_institution_feature", table_name="prompt_templates")
    op.drop_table("prompt_templates")
    op.drop_index("ix_ai_usage_logs_institution_day", table_name="ai_usage_logs")
    op.drop_index("ix_ai_usage_logs_institution_user_created", table_name="ai_usage_logs")
    op.drop_table("ai_usage_logs")
    op.drop_table("institution_ai_limits")
    op.drop_index("ix_ai_model_configs_institution_active", table_name="ai_model_configs")
    op.drop_table("ai_model_configs")
