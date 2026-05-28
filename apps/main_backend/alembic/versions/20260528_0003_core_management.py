"""core management foundation

Revision ID: 20260528_0003
Revises: 20260528_0002
Create Date: 2026-05-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260528_0003"
down_revision: Union[str, None] = "20260528_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "institution_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False, server_default="Asia/Katmandu"),
        sa.Column("locale", sa.String(length=20), nullable=False, server_default="en"),
        sa.Column("grading_settings", postgresql.JSONB()),
        sa.Column("notification_settings", postgresql.JSONB()),
        sa.Column("security_settings", postgresql.JSONB()),
        sa.Column("ai_settings", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", name="uq_institution_settings_institution_id"),
    )

    op.create_table(
        "branches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("code", sa.String(length=40)),
        sa.Column("address", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", "name", name="uq_branches_institution_name"),
    )
    op.create_index("ix_branches_institution", "branches", ["institution_id"])

    op.create_table(
        "academic_years",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", "name", name="uq_academic_years_institution_name"),
    )
    op.create_index("ix_academic_years_institution", "academic_years", ["institution_id"])

    op.create_table(
        "classes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("grade_level", sa.Integer()),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", "name", name="uq_classes_institution_name"),
    )
    op.create_index("ix_classes_institution", "classes", ["institution_id"])

    op.create_table(
        "sections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("capacity", sa.Integer()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", "class_id", "name", name="uq_sections_institution_class_name"),
    )
    op.create_index("ix_sections_institution_class", "sections", ["institution_id", "class_id"])

    op.create_table(
        "subjects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", "code", name="uq_subjects_institution_code"),
    )
    op.create_index("ix_subjects_institution", "subjects", ["institution_id"])

    op.create_table(
        "class_subjects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", "class_id", "subject_id", name="uq_class_subjects"),
    )
    op.create_index("ix_class_subjects_institution_class", "class_subjects", ["institution_id", "class_id"])

    op.create_table(
        "students",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("admission_number", sa.String(length=80), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("date_of_birth", sa.Date()),
        sa.Column("gender", sa.String(length=40)),
        sa.Column("current_class_id", postgresql.UUID(as_uuid=True)),
        sa.Column("current_section_id", postgresql.UUID(as_uuid=True)),
        sa.Column("roll_number", sa.String(length=40)),
        sa.Column("learning_profile", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["current_class_id"], ["classes.id"]),
        sa.ForeignKeyConstraint(["current_section_id"], ["sections.id"]),
        sa.UniqueConstraint("institution_id", "admission_number", name="uq_students_institution_admission"),
    )
    op.create_index("ix_students_institution_class", "students", ["institution_id", "current_class_id"])
    op.create_index("ix_students_institution_user", "students", ["institution_id", "user_id"])

    op.create_table(
        "teachers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("employee_code", sa.String(length=80), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=40)),
        sa.Column("metadata_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("institution_id", "employee_code", name="uq_teachers_institution_employee"),
    )
    op.create_index("ix_teachers_institution", "teachers", ["institution_id"])
    op.create_index("ix_teachers_institution_user", "teachers", ["institution_id", "user_id"])

    op.create_table(
        "parents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=40)),
        sa.Column("email", sa.String(length=320)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_parents_institution", "parents", ["institution_id"])
    op.create_index("ix_parents_institution_user", "parents", ["institution_id", "user_id"])

    op.create_table(
        "parent_student_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relationship", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["parent_id"], ["parents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("institution_id", "parent_id", "student_id", name="uq_parent_student_links"),
    )
    op.create_index("ix_parent_student_links_parent", "parent_student_links", ["institution_id", "parent_id"])
    op.create_index("ix_parent_student_links_student", "parent_student_links", ["institution_id", "student_id"])

    op.create_table(
        "teacher_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("section_id", postgresql.UUID(as_uuid=True)),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "institution_id",
            "teacher_id",
            "class_id",
            "section_id",
            "subject_id",
            name="uq_teacher_assignments_scope",
        ),
    )
    op.create_index("ix_teacher_assignments_teacher", "teacher_assignments", ["institution_id", "teacher_id"])
    op.create_index(
        "ix_teacher_assignments_class_subject",
        "teacher_assignments",
        ["institution_id", "class_id", "subject_id"],
    )

    op.create_table(
        "student_enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("academic_year_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("section_id", postgresql.UUID(as_uuid=True)),
        sa.Column("roll_number", sa.String(length=40)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["academic_year_id"], ["academic_years.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"]),
        sa.UniqueConstraint("institution_id", "student_id", "academic_year_id", name="uq_student_enrollment_year"),
    )
    op.create_index("ix_student_enrollments_class", "student_enrollments", ["institution_id", "class_id", "section_id"])


def downgrade() -> None:
    op.drop_index("ix_student_enrollments_class", table_name="student_enrollments")
    op.drop_table("student_enrollments")
    op.drop_index("ix_teacher_assignments_class_subject", table_name="teacher_assignments")
    op.drop_index("ix_teacher_assignments_teacher", table_name="teacher_assignments")
    op.drop_table("teacher_assignments")
    op.drop_index("ix_parent_student_links_student", table_name="parent_student_links")
    op.drop_index("ix_parent_student_links_parent", table_name="parent_student_links")
    op.drop_table("parent_student_links")
    op.drop_index("ix_parents_institution_user", table_name="parents")
    op.drop_index("ix_parents_institution", table_name="parents")
    op.drop_table("parents")
    op.drop_index("ix_teachers_institution_user", table_name="teachers")
    op.drop_index("ix_teachers_institution", table_name="teachers")
    op.drop_table("teachers")
    op.drop_index("ix_students_institution_user", table_name="students")
    op.drop_index("ix_students_institution_class", table_name="students")
    op.drop_table("students")
    op.drop_index("ix_class_subjects_institution_class", table_name="class_subjects")
    op.drop_table("class_subjects")
    op.drop_index("ix_subjects_institution", table_name="subjects")
    op.drop_table("subjects")
    op.drop_index("ix_sections_institution_class", table_name="sections")
    op.drop_table("sections")
    op.drop_index("ix_classes_institution", table_name="classes")
    op.drop_table("classes")
    op.drop_index("ix_academic_years_institution", table_name="academic_years")
    op.drop_table("academic_years")
    op.drop_index("ix_branches_institution", table_name="branches")
    op.drop_table("branches")
    op.drop_table("institution_settings")

