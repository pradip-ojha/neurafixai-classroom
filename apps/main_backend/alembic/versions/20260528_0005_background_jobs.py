"""background jobs and scheduler metadata

Revision ID: 20260528_0005
Revises: 20260528_0004
Create Date: 2026-05-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260528_0005"
down_revision: Union[str, None] = "20260528_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

job_status = postgresql.ENUM(
    "queued",
    "running",
    "retrying",
    "completed",
    "failed",
    "cancelled",
    name="background_job_status",
)


def upgrade() -> None:
    job_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "background_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("job_type", sa.String(length=120), nullable=False),
        sa.Column("queue_name", sa.String(length=80), nullable=False),
        sa.Column("status", job_status, nullable=False, server_default="queued"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("idempotency_key", sa.String(length=160)),
        sa.Column("celery_task_id", sa.String(length=160)),
        sa.Column("input_payload", postgresql.JSONB()),
        sa.Column("result_payload", postgresql.JSONB()),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("failed_at", sa.DateTime(timezone=True)),
        sa.Column("cancelled_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.UniqueConstraint("institution_id", "idempotency_key", name="uq_background_jobs_idempotency_key"),
    )
    op.create_index(
        "ix_background_jobs_institution_status_created",
        "background_jobs",
        ["institution_id", "status", "created_at"],
    )
    op.create_index(
        "ix_background_jobs_actor_created",
        "background_jobs",
        ["institution_id", "actor_user_id", "created_at"],
    )

    op.create_table(
        "job_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text()),
        sa.Column("payload", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["job_id"], ["background_jobs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_job_events_job_created", "job_events", ["institution_id", "job_id", "created_at"])

    op.create_table(
        "scheduled_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True)),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("job_type", sa.String(length=120), nullable=False),
        sa.Column("queue_name", sa.String(length=80), nullable=False),
        sa.Column("schedule", sa.String(length=160), nullable=False),
        sa.Column("payload", postgresql.JSONB()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_scheduled_jobs_institution_active", "scheduled_jobs", ["institution_id", "is_active"])


def downgrade() -> None:
    op.drop_index("ix_scheduled_jobs_institution_active", table_name="scheduled_jobs")
    op.drop_table("scheduled_jobs")
    op.drop_index("ix_job_events_job_created", table_name="job_events")
    op.drop_table("job_events")
    op.drop_index("ix_background_jobs_actor_created", table_name="background_jobs")
    op.drop_index("ix_background_jobs_institution_status_created", table_name="background_jobs")
    op.drop_table("background_jobs")
    job_status.drop(op.get_bind(), checkfirst=True)
