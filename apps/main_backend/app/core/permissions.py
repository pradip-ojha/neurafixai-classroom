from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class PermissionSeed:
    id: UUID
    code: str
    category: str
    description: str


_PERMISSION_ROWS = [
    ("00000000-0000-4000-8000-000000000001", "institution.manage", "institution", "Manage institution profile."),
    ("00000000-0000-4000-8000-000000000002", "institution.settings.manage", "institution", "Manage institution settings."),
    ("00000000-0000-4000-8000-000000000003", "users.create", "users", "Create users."),
    ("00000000-0000-4000-8000-000000000004", "users.read", "users", "Read users."),
    ("00000000-0000-4000-8000-000000000005", "users.update", "users", "Update users."),
    ("00000000-0000-4000-8000-000000000006", "users.delete", "users", "Delete users."),
    ("00000000-0000-4000-8000-000000000007", "roles.manage", "rbac", "Manage roles."),
    ("00000000-0000-4000-8000-000000000008", "permissions.manage", "rbac", "Manage permissions."),
    ("00000000-0000-4000-8000-000000000009", "permissions.read", "rbac", "Read permissions."),
    ("00000000-0000-4000-8000-000000000010", "students.create", "students", "Create students."),
    ("00000000-0000-4000-8000-000000000011", "students.read", "students", "Read students."),
    ("00000000-0000-4000-8000-000000000012", "students.update", "students", "Update students."),
    ("00000000-0000-4000-8000-000000000013", "students.delete", "students", "Delete students."),
    ("00000000-0000-4000-8000-000000000014", "teachers.manage", "teachers", "Manage teachers."),
    ("00000000-0000-4000-8000-000000000015", "parents.manage", "parents", "Manage parents."),
    ("00000000-0000-4000-8000-000000000016", "classes.manage", "academic", "Manage classes."),
    ("00000000-0000-4000-8000-000000000017", "sections.manage", "academic", "Manage sections."),
    ("00000000-0000-4000-8000-000000000018", "subjects.manage", "academic", "Manage subjects."),
    ("00000000-0000-4000-8000-000000000019", "syllabus.manage", "academic", "Manage syllabus."),
    ("00000000-0000-4000-8000-000000000020", "content.upload", "content", "Upload content."),
    ("00000000-0000-4000-8000-000000000021", "content.read", "content", "Read content."),
    ("00000000-0000-4000-8000-000000000022", "content.update", "content", "Update content."),
    ("00000000-0000-4000-8000-000000000023", "content.delete", "content", "Delete content."),
    ("00000000-0000-4000-8000-000000000024", "content.approve", "content", "Approve content."),
    ("00000000-0000-4000-8000-000000000025", "exams.create", "exams", "Create exams."),
    ("00000000-0000-4000-8000-000000000026", "exams.publish", "exams", "Publish exams."),
    ("00000000-0000-4000-8000-000000000027", "exams.evaluate", "exams", "Evaluate exams."),
    ("00000000-0000-4000-8000-000000000028", "questions.create", "questions", "Create questions."),
    ("00000000-0000-4000-8000-000000000029", "questions.approve", "questions", "Approve questions."),
    ("00000000-0000-4000-8000-000000000030", "reports.view", "reports", "View reports."),
    ("00000000-0000-4000-8000-000000000031", "reports.export", "reports", "Export reports."),
    ("00000000-0000-4000-8000-000000000032", "ai_tutor.use", "ai", "Use AI tutor."),
    ("00000000-0000-4000-8000-000000000033", "ai_tutor.configure", "ai", "Configure AI tutor."),
    ("00000000-0000-4000-8000-000000000034", "ai_content.generate", "ai", "Generate AI content."),
    ("00000000-0000-4000-8000-000000000035", "billing.view", "billing", "View billing."),
    ("00000000-0000-4000-8000-000000000036", "audit_logs.view", "audit", "View audit logs."),
    ("00000000-0000-4000-8000-000000000037", "security_events.view", "security", "View security events."),
    ("00000000-0000-4000-8000-000000000038", "settings.manage", "settings", "Manage settings."),
    ("00000000-0000-4000-8000-000000000039", "files.upload", "files", "Upload files."),
    ("00000000-0000-4000-8000-000000000040", "files.download", "files", "Download files."),
    ("00000000-0000-4000-8000-000000000041", "jobs.read", "jobs", "Read background jobs."),
    ("00000000-0000-4000-8000-000000000042", "jobs.manage", "jobs", "Manage background jobs."),
    ("00000000-0000-4000-8000-000000000043", "knowledge.read", "knowledge", "Read knowledge bases and documents."),
    ("00000000-0000-4000-8000-000000000044", "knowledge.manage", "knowledge", "Manage knowledge bases and ingestion."),
]

DEFAULT_PERMISSIONS = [
    PermissionSeed(id=UUID(row[0]), code=row[1], category=row[2], description=row[3])
    for row in _PERMISSION_ROWS
]

DEFAULT_PERMISSION_CODES = tuple(permission.code for permission in DEFAULT_PERMISSIONS)
INSTITUTION_OWNER_ROLE_SLUG = "institution-owner"
