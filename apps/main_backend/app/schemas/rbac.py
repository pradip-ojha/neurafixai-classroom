from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PermissionData(BaseModel):
    id: UUID
    code: str
    category: str
    description: str | None

    model_config = {"from_attributes": True}


class RoleData(BaseModel):
    id: UUID
    institution_id: UUID | None
    name: str
    slug: str
    description: str | None
    is_system: bool

    model_config = {"from_attributes": True}


class CurrentPermissionsData(BaseModel):
    institution_id: UUID
    user_id: UUID
    permissions: list[str]


class AuditLogData(BaseModel):
    id: UUID
    institution_id: UUID | None
    actor_user_id: UUID | None
    action: str
    entity_type: str | None
    entity_id: UUID | None
    old_values: dict | None
    new_values: dict | None
    metadata_json: dict | None
    request_id: str | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
