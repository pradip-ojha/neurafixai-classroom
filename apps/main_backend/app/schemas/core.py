from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class PaginationParams(BaseModel):
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class InstitutionData(BaseModel):
    id: UUID
    name: str
    slug: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InstitutionUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)


class InstitutionSettingsData(BaseModel):
    id: UUID
    institution_id: UUID
    timezone: str
    locale: str
    grading_settings: dict | None
    notification_settings: dict | None
    security_settings: dict | None
    ai_settings: dict | None

    model_config = {"from_attributes": True}


class UserListData(BaseModel):
    id: UUID
    institution_id: UUID
    email: EmailStr
    status: str
    email_verified_at: datetime | None
    last_login_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BranchCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    code: str | None = Field(default=None, max_length=40)
    address: str | None = None


class BranchData(BranchCreateRequest):
    id: UUID
    institution_id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AcademicYearCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    starts_on: date
    ends_on: date
    is_current: bool = False


class AcademicYearData(AcademicYearCreateRequest):
    id: UUID
    institution_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ClassCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    grade_level: int | None = Field(default=None, ge=0, le=20)
    description: str | None = None


class ClassData(ClassCreateRequest):
    id: UUID
    institution_id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SectionCreateRequest(BaseModel):
    class_id: UUID
    name: str = Field(min_length=1, max_length=80)
    capacity: int | None = Field(default=None, ge=1)


class SectionData(SectionCreateRequest):
    id: UUID
    institution_id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SubjectCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    code: str = Field(min_length=1, max_length=40)
    description: str | None = None


class SubjectData(SubjectCreateRequest):
    id: UUID
    institution_id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentCreateRequest(BaseModel):
    admission_number: str = Field(min_length=1, max_length=80)
    full_name: str = Field(min_length=2, max_length=255)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=40)
    current_class_id: UUID | None = None
    current_section_id: UUID | None = None
    roll_number: str | None = Field(default=None, max_length=40)
    learning_profile: dict | None = None


class StudentData(StudentCreateRequest):
    id: UUID
    institution_id: UUID
    user_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TeacherCreateRequest(BaseModel):
    employee_code: str = Field(min_length=1, max_length=80)
    full_name: str = Field(min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=40)
    metadata_json: dict | None = None


class TeacherData(TeacherCreateRequest):
    id: UUID
    institution_id: UUID
    user_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ParentCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None


class ParentData(ParentCreateRequest):
    id: UUID
    institution_id: UUID
    user_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}

