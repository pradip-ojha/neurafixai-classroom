from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_permission
from app.core.tenant import TenantContext
from app.db.session import get_db
from app.repositories.core_repository import CoreRepository
from app.schemas.common import ApiResponse
from app.schemas.core import (
    AcademicYearCreateRequest,
    AcademicYearData,
    BranchCreateRequest,
    BranchData,
    ClassCreateRequest,
    ClassData,
    InstitutionData,
    InstitutionSettingsData,
    InstitutionUpdateRequest,
    ParentCreateRequest,
    ParentData,
    SectionCreateRequest,
    SectionData,
    StudentCreateRequest,
    StudentData,
    SubjectCreateRequest,
    SubjectData,
    TeacherCreateRequest,
    TeacherData,
    UserListData,
)
from app.services.audit_service import AuditService
from app.services.core_service import CoreService

router = APIRouter(tags=["core-management"])


@router.get("/institutions/me", response_model=ApiResponse[InstitutionData])
async def get_my_institution(
    request: Request,
    tenant: TenantContext = Depends(require_permission("institution.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[InstitutionData]:
    institution = await CoreService(db).get_institution(tenant.institution_id)
    return _response(request, InstitutionData.model_validate(institution), "Institution loaded.")


@router.patch("/institutions/me", response_model=ApiResponse[InstitutionData])
async def update_my_institution(
    payload: InstitutionUpdateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("institution.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[InstitutionData]:
    institution = await CoreService(db).update_institution(tenant.institution_id, name=payload.name)
    AuditService(db).record(
        action="institution.updated",
        institution_id=tenant.institution_id,
        actor_user_id=tenant.user_id,
        entity_type="institution",
        entity_id=institution.id,
        new_values=payload.model_dump(exclude_none=True),
        request_id=request.state.request_id,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    await db.commit()
    return _response(request, InstitutionData.model_validate(institution), "Institution updated.")


@router.get("/settings/institution", response_model=ApiResponse[InstitutionSettingsData])
async def get_institution_settings(
    request: Request,
    tenant: TenantContext = Depends(require_permission("institution.settings.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[InstitutionSettingsData]:
    settings = await CoreService(db).get_or_create_settings(tenant.institution_id)
    return _response(request, InstitutionSettingsData.model_validate(settings), "Settings loaded.")


@router.get("/users", response_model=ApiResponse[list[UserListData]])
async def list_users(
    request: Request,
    tenant: TenantContext = Depends(require_permission("users.read")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> ApiResponse[list[UserListData]]:
    users = await CoreRepository(db).list_users(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [UserListData.model_validate(user) for user in users], "Users loaded.")


@router.get("/branches", response_model=ApiResponse[list[BranchData]])
async def list_branches(
    request: Request,
    tenant: TenantContext = Depends(require_permission("institution.manage")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> ApiResponse[list[BranchData]]:
    rows = await CoreRepository(db).list_branches(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [BranchData.model_validate(row) for row in rows], "Branches loaded.")


@router.post("/branches", response_model=ApiResponse[BranchData], status_code=201)
async def create_branch(
    payload: BranchCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("institution.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[BranchData]:
    row = await CoreService(db).create_branch(tenant.institution_id, **payload.model_dump())
    await _audit_create(db, request, tenant, "branch", row.id, payload.model_dump())
    return _response(request, BranchData.model_validate(row), "Branch created.")


@router.get("/academic-years", response_model=ApiResponse[list[AcademicYearData]])
async def list_academic_years(
    request: Request,
    tenant: TenantContext = Depends(require_permission("settings.manage")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> ApiResponse[list[AcademicYearData]]:
    rows = await CoreRepository(db).list_academic_years(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [AcademicYearData.model_validate(row) for row in rows], "Academic years loaded.")


@router.post("/academic-years", response_model=ApiResponse[AcademicYearData], status_code=201)
async def create_academic_year(
    payload: AcademicYearCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("settings.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AcademicYearData]:
    row = await CoreService(db).create_academic_year(tenant.institution_id, **payload.model_dump())
    await _audit_create(db, request, tenant, "academic_year", row.id, payload.model_dump(mode="json"))
    return _response(request, AcademicYearData.model_validate(row), "Academic year created.")


@router.get("/classes", response_model=ApiResponse[list[ClassData]])
async def list_classes(
    request: Request,
    tenant: TenantContext = Depends(require_permission("classes.manage")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> ApiResponse[list[ClassData]]:
    rows = await CoreRepository(db).list_classes(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [ClassData.model_validate(row) for row in rows], "Classes loaded.")


@router.post("/classes", response_model=ApiResponse[ClassData], status_code=201)
async def create_class(
    payload: ClassCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("classes.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ClassData]:
    row = await CoreService(db).create_class(tenant.institution_id, **payload.model_dump())
    await _audit_create(db, request, tenant, "class", row.id, payload.model_dump())
    return _response(request, ClassData.model_validate(row), "Class created.")


@router.get("/sections", response_model=ApiResponse[list[SectionData]])
async def list_sections(
    request: Request,
    tenant: TenantContext = Depends(require_permission("sections.manage")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> ApiResponse[list[SectionData]]:
    rows = await CoreRepository(db).list_sections(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [SectionData.model_validate(row) for row in rows], "Sections loaded.")


@router.post("/sections", response_model=ApiResponse[SectionData], status_code=201)
async def create_section(
    payload: SectionCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("sections.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[SectionData]:
    row = await CoreService(db).create_section(tenant.institution_id, **payload.model_dump())
    await _audit_create(db, request, tenant, "section", row.id, payload.model_dump(mode="json"))
    return _response(request, SectionData.model_validate(row), "Section created.")


@router.get("/subjects", response_model=ApiResponse[list[SubjectData]])
async def list_subjects(
    request: Request,
    tenant: TenantContext = Depends(require_permission("subjects.manage")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> ApiResponse[list[SubjectData]]:
    rows = await CoreRepository(db).list_subjects(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [SubjectData.model_validate(row) for row in rows], "Subjects loaded.")


@router.post("/subjects", response_model=ApiResponse[SubjectData], status_code=201)
async def create_subject(
    payload: SubjectCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("subjects.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[SubjectData]:
    row = await CoreService(db).create_subject(tenant.institution_id, **payload.model_dump())
    await _audit_create(db, request, tenant, "subject", row.id, payload.model_dump())
    return _response(request, SubjectData.model_validate(row), "Subject created.")


@router.get("/students", response_model=ApiResponse[list[StudentData]])
async def list_students(
    request: Request,
    tenant: TenantContext = Depends(require_permission("students.read")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> ApiResponse[list[StudentData]]:
    rows = await CoreRepository(db).list_students(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [StudentData.model_validate(row) for row in rows], "Students loaded.")


@router.post("/students", response_model=ApiResponse[StudentData], status_code=201)
async def create_student(
    payload: StudentCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("students.create")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[StudentData]:
    row = await CoreService(db).create_student(tenant.institution_id, **payload.model_dump())
    await _audit_create(db, request, tenant, "student", row.id, payload.model_dump(mode="json"))
    return _response(request, StudentData.model_validate(row), "Student created.")


@router.get("/teachers", response_model=ApiResponse[list[TeacherData]])
async def list_teachers(
    request: Request,
    tenant: TenantContext = Depends(require_permission("teachers.manage")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> ApiResponse[list[TeacherData]]:
    rows = await CoreRepository(db).list_teachers(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [TeacherData.model_validate(row) for row in rows], "Teachers loaded.")


@router.post("/teachers", response_model=ApiResponse[TeacherData], status_code=201)
async def create_teacher(
    payload: TeacherCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("teachers.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TeacherData]:
    row = await CoreService(db).create_teacher(tenant.institution_id, **payload.model_dump())
    await _audit_create(db, request, tenant, "teacher", row.id, payload.model_dump())
    return _response(request, TeacherData.model_validate(row), "Teacher created.")


@router.get("/parents", response_model=ApiResponse[list[ParentData]])
async def list_parents(
    request: Request,
    tenant: TenantContext = Depends(require_permission("parents.manage")),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> ApiResponse[list[ParentData]]:
    rows = await CoreRepository(db).list_parents(tenant.institution_id, _limit(limit), _offset(offset))
    return _response(request, [ParentData.model_validate(row) for row in rows], "Parents loaded.")


@router.post("/parents", response_model=ApiResponse[ParentData], status_code=201)
async def create_parent(
    payload: ParentCreateRequest,
    request: Request,
    tenant: TenantContext = Depends(require_permission("parents.manage")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ParentData]:
    row = await CoreService(db).create_parent(tenant.institution_id, **payload.model_dump())
    await _audit_create(db, request, tenant, "parent", row.id, payload.model_dump())
    return _response(request, ParentData.model_validate(row), "Parent created.")


def _response(request: Request, data, message: str):
    return ApiResponse(data=data, message=message, request_id=request.state.request_id)


async def _audit_create(
    db: AsyncSession,
    request: Request,
    tenant: TenantContext,
    entity_type: str,
    entity_id,
    values: dict,
) -> None:
    AuditService(db).record(
        action=f"{entity_type}.created",
        institution_id=tenant.institution_id,
        actor_user_id=tenant.user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        new_values=values,
        request_id=request.state.request_id,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    await db.commit()


def _limit(value: int) -> int:
    return max(1, min(value, 100))


def _offset(value: int) -> int:
    return max(0, value)


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else None

